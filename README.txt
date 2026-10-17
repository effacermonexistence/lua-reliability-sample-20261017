Lua — synthetic workflow reliability sample

This code was generated and locally tested by an AI assistant for a new service experiment. It is not a client case study, production integration, benchmark uplift, or evidence of paid delivery.

Contents
- faq_bot_demo.py: a local in-memory FAQ/event state machine; no network calls.
- test_faq_bot_demo.py: 15 deterministic tests.
- faq_bot_verification.txt: recorded local test run and synthetic trace.

Run with Python 3 standard library, from the folder containing these files:
  python3 -m unittest -v test_faq_bot_demo.py
  python3 faq_bot_demo.py --demo

The tests cover malformed inputs, per-contact duplicate-message suppression within one running process, STOP/START state, unknown-FAQ handoff, separation between contacts, and booking confirmation only when a matching injected trusted receipt exists.

The demo returns drafts or queue decisions. It does not receive real webhooks, call Meta/WhatsApp/n8n, send messages, authenticate requests, persist state, or prove safety of free-form LLM outputs. Restart-safe deduplication and any live integration would require separate implementation and tests.

A real workflow review starts from the buyer's own rules and authorized synthetic/redacted test data. No passwords or private customer records are needed for this sample.
