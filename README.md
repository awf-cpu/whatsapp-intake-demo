# whatsapp-intake-demo

[![CI](https://github.com/awf-cpu/whatsapp-intake-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/awf-cpu/whatsapp-intake-demo/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A **guarded intake bot** for messaging channels (WhatsApp-style), demonstrated on a fictional dental clinic. It runs with a **simulated model provider**: no network, no API keys, fully deterministic and testable. The point is the architecture around the model, not the model.

## The business problem

Putting an LLM in front of customers is a liability question. The model can promise results, invent prices, play doctor, or claim to be a person. Regulated businesses (health, legal, finance) need the **rules to be code, not a prompt the model may ignore**.

## Design

- **Deterministic control flow.** A state machine decides what happens (collect name, reason, preferred time). The model only phrases friendly lines.
- **Output guards on every reply.** Rules block guarantees, diagnoses, prescriptions, invented prices, "I am a real dentist" claims, contact-data leaks and over-long replies. A blocked reply is swapped for a safe fallback and the chat is **handed off to a human**.
- **Honesty about being automated.** "Are you a bot?" is answered by a fixed, truthful line before the model is ever consulted.
- **Human handoff and silence.** Asking for a person, or an emergency keyword, hands the chat to staff and the bot stops talking.
- **Opt-out is permanent.** `STOP` ends all messages in that session.
- **Provider interface.** Swap `SimulatedProvider` for a real LLM client implementing `reply(stage, text)`; guards and flow stay the same.

## Try it

```bash
python -m intake                     # chat in the terminal
python -m intake --misbehave price   # simulate a model that invents a price and watch the guard fire
pip install pytest && pytest -q      # 9 tests
```

Example with a misbehaving model:

```
bot: I'm an automated assistant for Bright Smile Dental. ... What is your name?
you: Ana
you: cleaning
bot: Let me bring in a team member to help you with that. They will reply here shortly.
[guard blocked: invented_price; handed off to a human]
```

## Scope and honesty

Regex guards are a first layer, not a complete safety system; production use adds an evaluation set, logging and human review. The clinic and all data here are fictional.

MIT licensed. Built by André Feix · [LinkedIn](https://www.linkedin.com/in/andrefeix)
