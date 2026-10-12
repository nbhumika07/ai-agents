"""Interactive CLI for the stateful travel-agent state machine."""
from datetime import date
from pathlib import Path
import sys

from pydantic import ValidationError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from .agent import StatefulTravelAgent
from .memory import MemoryStore, PreferenceMemory, ShortTermMemory
from .models import AgentState, Phase, TravelGoal


def main() -> None:
    memory_store = MemoryStore(Path(__file__).with_name("long_term_memory.json"))
    long_term = memory_store.load()
    thread = ShortTermMemory()
    print("Stateful Travel Agent (fictional demo inventory; no real booking/payment)")
    try:
        origin = input("Origin city: ").strip()
        destination = input("Destination city: ").strip()
        travel_date = date.fromisoformat(input("Travel date (YYYY-MM-DD): ").strip())
        nights = int(input("Nights: ").strip())
        total_budget = float(input("Total trip budget (INR): ").strip())
        nightly_cap = float(input("Initial hotel nightly cap (INR): ").strip())
        max_cap = float(input("Maximum nightly cap you permit during re-planning (INR): ").strip())
        amenities = [a.strip() for a in input("Required hotel amenities (comma-separated, optional): ").split(",") if a.strip()]
        airlines = [a.strip() for a in input("Preferred airlines (comma-separated, optional): ").split(",") if a.strip()]
        date_shift = int(input("Maximum date shift in days (0-14): ").strip() or "0")
        goal = TravelGoal(origin=origin, destination=destination, travel_date=travel_date, nights=nights,
            total_budget=min(total_budget, long_term.preferences.budget_ceiling or total_budget),
            initial_nightly_cap=nightly_cap, max_nightly_cap=max(max_cap, nightly_cap),
            max_date_shift_days=date_shift, required_amenities=amenities)
    except (ValueError, ValidationError) as exc:
        print(f"Invalid trip details: {exc}")
        return

    thread.add_message("user", f"Trip request: {goal.model_dump_json()}")
    agent = StatefulTravelAgent()
    state = agent.start(AgentState(goal=goal, messages=thread.messages.copy()), long_term)
    state = agent.run_until_interrupt(state)

    if state.phase == Phase.FAILED:
        print(f"No itinerary found: {state.error}")
        return
    if state.phase == Phase.HUMAN_APPROVAL_GATE and state.proposal:
        proposal = state.proposal
        print("\nTRANSACTION REVIEW")
        print(f"Route: {proposal.flight.origin} → {proposal.flight.destination} on {proposal.flight.travel_date}")
        print(f"Flight: {proposal.flight.airline} ({proposal.flight.flight_id}) — ₹{proposal.flight.price:.2f}")
        print(f"Hotel: {proposal.hotel.name} ({proposal.hotel.hotel_id}) — ₹{proposal.hotel.nightly_price:.2f}/night × {proposal.nights}")
        print(f"Total: ₹{proposal.total_cost:.2f} INR (budget ₹{goal.total_budget:.2f})")
        print(f"Required amenities: {', '.join(goal.required_amenities) or 'none'}")
        decision = input("Type approve or deny: ").strip().casefold()
        if decision not in {"approve", "deny"}:
            print("Approval was not explicit. Transaction denied safely.")
            decision = "deny"
        state = agent.resume_after_approval(state, decision)

    if state.booking_receipt:
        print(f"\nCompleted: simulated confirmation {state.booking_receipt['booking_id']}.")
        # Save only preferences explicitly carried into this request; never expand user limits.
        memory_store.remember_preferences(PreferenceMemory(
            budget_ceiling=goal.total_budget,
            hotel_amenities=goal.required_amenities,
            preferred_airlines=airlines,
        ))
    elif state.approval_decision == "deny":
        print("\nDenied. No transaction was executed.")


if __name__ == "__main__":
    main()
