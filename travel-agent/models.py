from __future__ import annotations

from datetime import date, timedelta
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class Phase(str, Enum):
    START = "START"
    AGENT_REASONING = "agent_reasoning"
    EXECUTE_TOOLS = "execute_tools"
    PROCESS_OBSERVATION = "process_observation"
    HUMAN_APPROVAL_GATE = "human_approval_gate"
    FINALIZE_ACTION = "finalize_action"
    END = "END"
    FAILED = "FAILED"


class TravelGoal(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    origin: str = Field(min_length=2)
    destination: str = Field(min_length=2)
    travel_date: date
    nights: int = Field(ge=1, le=30)
    total_budget: float = Field(gt=0)
    initial_nightly_cap: float = Field(gt=0)
    max_nightly_cap: float = Field(gt=0)
    max_date_shift_days: int = Field(default=0, ge=0, le=14)
    required_amenities: list[str] = Field(default_factory=list)


class Flight(BaseModel):
    flight_id: str
    origin: str
    destination: str
    travel_date: date
    price: float = Field(ge=0)
    airline: str
    available: bool = True


class Hotel(BaseModel):
    hotel_id: str
    location: str
    name: str
    nightly_price: float = Field(ge=0)
    amenities: list[str]
    available: bool = True


class TransactionProposal(BaseModel):
    flight: Flight
    hotel: Hotel
    nights: int
    total_cost: float
    currency: str = "INR"


class ToolEvent(BaseModel):
    tool_name: str
    tool_input: dict[str, Any]
    observation: str
    ok: bool


class AgentState(BaseModel):
    """Explicit, serializable state for one agent run."""
    goal: TravelGoal
    phase: Phase = Phase.START
    messages: list[dict[str, str]] = Field(default_factory=list)
    tool_history: list[ToolEvent] = Field(default_factory=list)
    accumulated_context: dict[str, Any] = Field(default_factory=dict)
    current_date: date | None = None
    current_nightly_cap: float | None = None
    retry_count: int = 0
    max_retries: int = 2
    last_observation: str = ""
    proposal: TransactionProposal | None = None
    approval_decision: str | None = None
    booking_receipt: dict[str, Any] | None = None
    error: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.current_date is None:
            self.current_date = self.goal.travel_date
        if self.current_nightly_cap is None:
            self.current_nightly_cap = self.goal.initial_nightly_cap
