from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field


class PreferenceMemory(BaseModel):
    budget_ceiling: float | None = None
    preferred_airlines: list[str] = Field(default_factory=list)
    hotel_amenities: list[str] = Field(default_factory=list)
    seat_preference: str | None = None
    meal_preference: str | None = None


class ShortTermMemory(BaseModel):
    """Conversation messages and scratchpad for the active thread."""
    messages: list[dict[str, str]] = Field(default_factory=list)
    scratchpad: list[str] = Field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-20:]


class LongTermMemory(BaseModel):
    """User preferences persisted between runs."""
    preferences: PreferenceMemory = Field(default_factory=PreferenceMemory)


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> LongTermMemory:
        if not self.path.exists():
            return LongTermMemory()
        try:
            return LongTermMemory.model_validate_json(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return LongTermMemory()

    def save(self, memory: LongTermMemory) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(memory.model_dump_json(indent=2), encoding="utf-8")

    def remember_preferences(self, preferences: PreferenceMemory) -> LongTermMemory:
        memory = self.load()
        old = memory.preferences.model_dump()
        new = preferences.model_dump(exclude_none=True)
        for key, value in new.items():
            if value not in (None, [], ""):
                old[key] = value
        memory.preferences = PreferenceMemory.model_validate(old)
        self.save(memory)
        return memory
