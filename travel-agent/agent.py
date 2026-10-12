from __future__ import annotations

from datetime import timedelta
from typing import Any
from pydantic import ValidationError

from .memory import LongTermMemory
from .models import AgentState, Phase, ToolEvent, TransactionProposal
from .llm import get_reflection_engine
from .tools import ToolRegistry


class StatefulTravelAgent:
    """Bounded state machine. Tool selection is deterministic and policy checked."""
    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.tools = registry or ToolRegistry()
        self.reflection = get_reflection_engine()

    def start(self, state: AgentState, memory: LongTermMemory) -> AgentState:
        if state.phase != Phase.START:
            raise ValueError("Agent must start in START phase.")
        state.phase = Phase.AGENT_REASONING
        state.messages.append({"role": "assistant", "content": "Reviewing request and saved preferences."})
        prefs = memory.preferences
        state.accumulated_context["preferred_airlines"] = prefs.preferred_airlines
        state.goal.required_amenities = sorted(set(state.goal.required_amenities + prefs.hotel_amenities))
        if prefs.budget_ceiling is not None:
            state.goal.total_budget = min(state.goal.total_budget, prefs.budget_ceiling)
        return state

    def run_until_interrupt(self, state: AgentState) -> AgentState:
        """Advance states until approval is required or the run reaches a terminal state."""
        while state.phase not in {Phase.HUMAN_APPROVAL_GATE, Phase.END, Phase.FAILED}:
            if state.phase == Phase.AGENT_REASONING:
                self._reason(state)
            elif state.phase == Phase.EXECUTE_TOOLS:
                self._execute_searches(state)
            elif state.phase == Phase.PROCESS_OBSERVATION:
                self._process_observation(state)
            elif state.phase == Phase.FINALIZE_ACTION:
                self._finalize(state)
            else:
                state.phase = Phase.FAILED
                state.error = f"Unexpected phase: {state.phase}"
        return state

    def _reason(self, state: AgentState) -> None:
        state.phase = Phase.EXECUTE_TOOLS
        state.accumulated_context["next_action"] = "search_flights_and_hotels"
        state.messages.append({"role": "assistant", "content": "Search options under active constraints."})

    def _execute_searches(self, state: AgentState) -> None:
        goal = state.goal
        state.error = None
        state.accumulated_context.pop("flights", None)
        state.accumulated_context.pop("hotels", None)
        try:
            flight_tool = self.tools.get("search_flights")
            hotel_tool = self.tools.get("search_hotels")
            search_date = state.current_date or goal.travel_date
            nightly_cap = state.current_nightly_cap if state.current_nightly_cap is not None else goal.initial_nightly_cap
            flights = flight_tool(goal.origin, goal.destination, search_date, goal.total_budget)
            hotels = hotel_tool(goal.destination, nightly_cap, goal.required_amenities)
            state.accumulated_context["flights"] = flights
            state.accumulated_context["hotels"] = hotels
            observation = f"Flight search returned {len(flights)} option(s); hotel search returned {len(hotels)} option(s)."
            state.tool_history.extend([
                ToolEvent(tool_name="search_flights", tool_input={"origin": goal.origin, "destination": goal.destination,
                    "date": str(search_date), "max_price": goal.total_budget}, observation=f"{len(flights)} result(s)", ok=True),
                ToolEvent(tool_name="search_hotels", tool_input={"location": goal.destination,
                    "max_nightly_price": nightly_cap, "required_amenities": goal.required_amenities},
                    observation=f"{len(hotels)} result(s)", ok=True),
            ])
            state.last_observation = observation
        except Exception as exc:
            state.last_observation = f"Tool failure: {exc}"
            state.error = str(exc)
            state.tool_history.append(ToolEvent(tool_name="search", tool_input={}, observation=state.last_observation, ok=False))
        state.phase = Phase.PROCESS_OBSERVATION

    def _process_observation(self, state: AgentState) -> None:
        flights = state.accumulated_context.get("flights", [])
        hotels = state.accumulated_context.get("hotels", [])
        options: list[tuple[Any, Any, float]] = []
        for flight in flights:
            for hotel in hotels:
                total = flight.price + hotel.nightly_price * state.goal.nights
                if total <= state.goal.total_budget:
                    options.append((flight, hotel, total))
        if options:
            preferred = {name.casefold() for name in state.accumulated_context.get("preferred_airlines", [])}
            flight, hotel, total = min(options, key=lambda option: (0 if option[0].airline.casefold() in preferred else 1, option[2]))
            state.proposal = TransactionProposal(flight=flight, hotel=hotel, nights=state.goal.nights, total_cost=total)
            state.last_observation = f"Best matching combination totals ₹{total:.2f}, within the ₹{state.goal.total_budget:.2f} ceiling."
            state.phase = Phase.HUMAN_APPROVAL_GATE
            state.messages.append({"role": "assistant", "content": state.last_observation})
            return

        if state.error:
            reason = f"Search tool failed: {state.error}"
            adjustment = "retry the search once"
        elif not flights:
            reason = "No demo flight options matched this route and fare limit."
            current_date = state.current_date or state.goal.travel_date
            next_shift = (current_date - state.goal.travel_date).days + 1
            if next_shift > state.goal.max_date_shift_days:
                state.phase = Phase.FAILED
                state.error = reason + " No date changes are permitted or available."
                return
            state.current_date = state.goal.travel_date + timedelta(days=next_shift)
            adjustment = f"shift the date by {next_shift} day(s), within the authorized window"
        elif not hotels:
            reason = "No hotel matched the nightly cap and required amenities."
            current_cap = state.current_nightly_cap if state.current_nightly_cap is not None else state.goal.initial_nightly_cap
            if current_cap >= state.goal.max_nightly_cap:
                state.phase = Phase.FAILED
                state.error = reason + " The user-authorized maximum nightly cap has been reached."
                return
            state.current_nightly_cap = min(state.goal.max_nightly_cap, current_cap + 2500)
            adjustment = f"raise nightly cap to ₹{state.current_nightly_cap:.2f}, within the authorized maximum"
        else:
            reason = "Flight and hotel options were found, but every combination exceeds the total budget."
            state.phase = Phase.FAILED
            state.error = reason + " No constraint was relaxed because the total budget is a hard limit."
            return

        if state.retry_count >= state.max_retries:
            state.phase = Phase.FAILED
            state.error = f"{reason} Re-plan limit ({state.max_retries}) reached."
            return
        state.last_observation = reason
        state.retry_count += 1
        constraints = (f"total budget ₹{state.goal.total_budget:.2f}; maximum nightly cap "
                       f"₹{state.goal.max_nightly_cap:.2f}; date shift at most {state.goal.max_date_shift_days} day(s)")
        try:
            rationale = self.reflection.reflect(reason, constraints)
        except Exception:
            rationale = reason
        state.accumulated_context["reflection"] = f"{rationale} Re-plan: {adjustment}; preserve all hard limits."
        state.messages.append({"role": "assistant", "content": state.accumulated_context["reflection"]})
        state.phase = Phase.AGENT_REASONING

    def resume_after_approval(self, state: AgentState, decision: str) -> AgentState:
        """Resume the interrupted run with an explicit approve or deny decision."""
        if state.phase != Phase.HUMAN_APPROVAL_GATE or state.proposal is None:
            raise ValueError("There is no pending transaction to approve.")
        normalized = decision.strip().casefold()
        if normalized not in {"approve", "deny"}:
            raise ValueError("Decision must be exactly 'approve' or 'deny'.")
        state.approval_decision = normalized
        state.accumulated_context["approval_payload"] = state.proposal.model_dump(mode="json")
        if normalized == "deny":
            state.messages.append({"role": "human", "content": "Transaction denied."})
            state.phase = Phase.END
            return state
        state.messages.append({"role": "human", "content": "Transaction approved."})
        state.phase = Phase.FINALIZE_ACTION
        return self.run_until_interrupt(state)

    def _finalize(self, state: AgentState) -> None:
        if state.approval_decision != "approve" or state.proposal is None:
            state.phase = Phase.FAILED
            state.error = "Safety gate blocked transaction: explicit approval is missing."
            return
        try:
            call = self.tools.get("execute_booking_transaction")
            proposal = state.proposal
            state.booking_receipt = call(proposal.flight.flight_id, proposal.hotel.hotel_id, proposal.total_cost)
            state.tool_history.append(ToolEvent(tool_name="execute_booking_transaction",
                tool_input={"flight_id": proposal.flight.flight_id, "hotel_id": proposal.hotel.hotel_id,
                    "total_cost": proposal.total_cost}, observation="Simulated transaction completed.", ok=True))
            state.phase = Phase.END
        except Exception as exc:
            state.error = f"Transaction failed: {exc}"
            state.phase = Phase.FAILED
