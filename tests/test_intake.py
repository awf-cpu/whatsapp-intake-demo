import pytest

from intake.flow import HONEST, SAFE_FALLBACK, IntakeBot, Session
from intake.guards import check_reply
from intake.provider import SimulatedProvider


def run(bot, s, *msgs):
    return [bot.handle(s, m) for m in msgs]


def test_happy_path_collects_fields():
    bot, s = IntakeBot(SimulatedProvider()), Session()
    run(bot, s, "hi", "Ana", "my tooth hurts when I drink cold water", "Tuesday 3pm")
    assert s.stage == "done" and not s.handoff and not s.guard_events
    assert s.data == {"name": "Ana", "reason": "my tooth hurts when I drink cold water",
                      "preferred_time": "Tuesday 3pm"}


@pytest.mark.parametrize("mode,rule", [("guarantee", "guarantee"), ("human", "claims_human"),
                                       ("price", "invented_price")])
def test_unsafe_model_output_is_blocked_and_handed_off(mode, rule):
    bot, s = IntakeBot(SimulatedProvider(misbehave=mode)), Session()
    out = run(bot, s, "hi", "Ana", "cleaning")[-1]
    assert out == SAFE_FALLBACK and s.handoff and s.guard_events == [rule]


def test_never_denies_being_automated():
    bot, s = IntakeBot(SimulatedProvider()), Session()
    assert bot.handle(s, "are you a bot?") == HONEST
    assert bot.handle(s, "am I talking to a real person?") == HONEST


def test_human_request_hands_off_then_bot_goes_silent():
    bot, s = IntakeBot(SimulatedProvider()), Session()
    assert bot.handle(s, "I want to talk to a receptionist") == SAFE_FALLBACK
    assert bot.handle(s, "hello?") == ""


def test_emergency_skips_the_flow():
    bot, s = IntakeBot(SimulatedProvider()), Session()
    out = bot.handle(s, "I have a swollen face")
    assert "urgent" in out and s.handoff


def test_stop_is_honored_permanently():
    bot, s = IntakeBot(SimulatedProvider()), Session()
    assert "unsubscribed" in bot.handle(s, "STOP")
    assert bot.handle(s, "hi again") == ""


def test_guards_reject_contact_leaks_and_length():
    assert not check_reply("Call me at +1 555 123 4567").ok
    assert not check_reply("mail dr@clinic.example").ok
    assert not check_reply("x" * 500).ok
    assert check_reply("Which day suits you?").ok
