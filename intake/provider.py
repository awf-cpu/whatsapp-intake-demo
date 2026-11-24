"""LLM provider interface plus a deterministic simulated provider (no network, no keys)."""
from __future__ import annotations

from typing import Protocol


class Provider(Protocol):
    def reply(self, stage: str, user_text: str) -> str: ...


class SimulatedProvider:
    """Stands in for a real model. `misbehave` makes it emit unsafe text so the
    guards can be demonstrated and tested."""

    def __init__(self, misbehave: str | None = None):
        self.misbehave = misbehave

    def reply(self, stage: str, user_text: str) -> str:
        if self.misbehave == "guarantee":
            return "We guarantee this treatment is 100% safe, no risk at all."
        if self.misbehave == "human":
            return "I am a real dentist and I can see you have an infection."
        if self.misbehave == "price":
            return "That will cost $450 for sure."
        return {
            "reason": "Thanks, that helps us prepare. Is it painful right now?",
            "time": "Got it. Which day and time suit you best?",
        }.get(stage, "Thank you.")
