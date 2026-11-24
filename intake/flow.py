"""Intake state machine for a fictional dental clinic ("Bright Smile").

Deterministic rules decide WHAT happens (opt-out, honesty about being a bot,
emergencies, handoff). The model only phrases the friendly lines, and every
line it produces is checked by the output guards first.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .guards import check_reply
from .provider import Provider

EMERGENCY = re.compile(r"\b(severe pain|swollen face|bleeding (a lot|heavily)|can't breathe|knocked out)\b", re.I)
ASKS_BOT = re.compile(r"\b(are you (a )?(bot|robot|ai|human|real person)|am i talking to)\b", re.I)
ASKS_HUMAN = re.compile(r"\b(human|real person|receptionist|talk to someone)\b", re.I)
STOP = re.compile(r"^\s*(stop|unsubscribe|cancel)\s*$", re.I)

SAFE_FALLBACK = "Let me bring in a team member to help you with that. They will reply here shortly."
HONEST = "I'm an automated assistant for Bright Smile Dental. I collect your details so the team can help faster."


@dataclass
class Session:
    stage: str = "start"           # start -> name -> reason -> time -> done
    data: dict = field(default_factory=dict)
    handoff: bool = False
    opted_out: bool = False
    guard_events: list[str] = field(default_factory=list)


class IntakeBot:
    def __init__(self, provider: Provider):
        self.provider = provider

    def handle(self, s: Session, text: str) -> str:
        if s.opted_out:
            return ""                                    # silence after STOP
        if STOP.match(text):
            s.opted_out = True
            return "You are unsubscribed. No more messages from us."
        if EMERGENCY.search(text):
            s.handoff = True
            return ("This sounds urgent. Please call the clinic now or go to the nearest "
                    "emergency room. A team member has been alerted.")
        if ASKS_BOT.search(text):
            return HONEST                                # never deny being automated
        if ASKS_HUMAN.search(text):
            s.handoff = True
            return SAFE_FALLBACK
        if s.handoff:
            return ""                                    # a human owns the chat now

        if s.stage == "start":
            s.stage = "name"
            return HONEST + " What is your name?"
        if s.stage == "name":
            s.data["name"] = text.strip()[:60]
            s.stage = "reason"
            return f"Nice to meet you, {s.data['name']}. What brings you in?"
        if s.stage == "reason":
            s.data["reason"] = text.strip()[:300]
            s.stage = "time"
            return self._guarded(s, "reason", text)
        if s.stage == "time":
            s.data["preferred_time"] = text.strip()[:80]
            s.stage = "done"
            return "Thanks! A team member will confirm your appointment here. Anything else to add?"
        return "Noted. The team will take it from here."

    def _guarded(self, s: Session, stage: str, text: str) -> str:
        draft = self.provider.reply(stage, text)
        verdict = check_reply(draft)
        if verdict.ok:
            return draft
        s.guard_events.append(verdict.rule or "unknown")
        s.handoff = True
        return SAFE_FALLBACK
