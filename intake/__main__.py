"""Terminal chat simulator: python -m intake [--misbehave guarantee|human|price]"""
import argparse

from .flow import IntakeBot, Session
from .provider import SimulatedProvider


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--misbehave", choices=["guarantee", "human", "price"])
    a = ap.parse_args()
    bot, s = IntakeBot(SimulatedProvider(a.misbehave)), Session()
    print("(type 'quit' to exit)")
    print("bot:", bot.handle(s, "hi"))
    while True:
        try:
            text = input("you: ")
        except EOFError:
            break
        if text.strip() == "quit":
            break
        out = bot.handle(s, text)
        if out:
            print("bot:", out)
        if s.guard_events:
            print(f"[guard blocked: {s.guard_events[-1]}; handed off to a human]")
    print("collected:", s.data)


if __name__ == "__main__":
    main()
