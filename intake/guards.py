"""Output guards: every model reply passes through these BEFORE it is sent.

The model is treated as untrusted. A reply that breaks any rule is replaced by a
safe fallback and the conversation is flagged for a human.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

MAX_LEN = 400

_RULES = [
    ("claims_human", re.compile(r"\b(i am a (real )?(human|person|dentist|nurse)|i'm a (real )?(human|person|dentist|nurse))\b", re.I)),
    ("guarantee", re.compile(r"\b(guarantee[sd]?|100% (safe|success)|no risk|always works)\b", re.I)),
    ("diagnosis", re.compile(r"\b(you (have|are suffering from)|your diagnosis|it is (definitely )?an? (infection|abscess|cavity))\b", re.I)),
    ("prescription", re.compile(r"\b(take \d+ ?mg|prescrib\w+|antibiotics?)\b", re.I)),
    ("invented_price", re.compile(r"\$\s?\d")),
    ("contact_leak", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d\s().-]{8,}\d")),
]


@dataclass
class GuardVerdict:
    ok: bool
    rule: str | None = None


def check_reply(text: str, allowed_prices: set[str] | None = None) -> GuardVerdict:
    if not text.strip():
        return GuardVerdict(False, "empty")
    if len(text) > MAX_LEN:
        return GuardVerdict(False, "too_long")
    for name, pattern in _RULES:
        if name == "invented_price" and allowed_prices:
            found = set(re.findall(r"\$\s?\d[\d,.]*", text))
            if found and found <= {p for p in allowed_prices}:
                continue
        if pattern.search(text):
            return GuardVerdict(False, name)
    return GuardVerdict(True)
