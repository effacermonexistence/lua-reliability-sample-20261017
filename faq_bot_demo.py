#!/usr/bin/env python3
"""Local-only, synthetic FAQ/webhook state-machine demo. No network or provider calls."""

import argparse
import json


class FAQBot:
    def __init__(self, booking_receipts=None):
        self.contacts = {}
        # Injected trusted state, never extracted from customer message text.
        self.booking_receipts = booking_receipts or {}

    def handle(self, event):
        if not isinstance(event, dict):
            return {"action": "reject", "reason": "malformed_event"}
        contact = event.get("contact_id")
        message = event.get("message_id")
        raw_text = event.get("text")
        if (not isinstance(contact, str) or not contact.strip()
                or not isinstance(message, str) or not message.strip()
                or not isinstance(raw_text, str) or not raw_text.strip()
                or len(raw_text) > 2000):
            return {"action": "reject", "reason": "malformed_event"}

        key = contact.strip()
        msg_id = message.strip()
        text = " ".join(raw_text.casefold().split())
        state = self.contacts.setdefault(key, {"seen": set(), "opted_out": False})
        if msg_id in state["seen"]:
            return {"action": "none", "reason": "duplicate_inbound"}
        state["seen"].add(msg_id)

        if text == "stop":
            state["opted_out"] = True
            return {"action": "none", "reason": "opted_out"}
        if text == "start":
            state["opted_out"] = False
            return {"action": "draft_reply", "text": "Message drafts are enabled again."}
        if state["opted_out"]:
            return {"action": "none", "reason": "opted_out"}

        if text in {"hours", "opening hours"}:
            return {"action": "draft_reply", "text": "Demo hours: Monday to Friday, 9:00–17:00."}
        if text in {"price", "pricing"}:
            return {"action": "draft_reply", "text": "Demo pricing: request a quote from the team."}
        if "book" in text or "appointment" in text:
            receipt = self.booking_receipts.get((key, msg_id))
            if receipt:
                return {"action": "draft_reply", "text": f"Booking confirmed in demo ledger: {receipt}."}
            return {"action": "draft_reply", "text": "Booking request noted; no booking is confirmed yet."}
        return {"action": "handoff_queue", "reason": "unknown_faq"}


def demo():
    bot = FAQBot()
    events = [
        {"contact_id": "demo-A", "message_id": "m1", "text": "hours"},
        {"contact_id": "demo-A", "message_id": "m1", "text": "hours"},
        {"contact_id": "demo-A", "message_id": "m2", "text": "STOP"},
        {"contact_id": "demo-A", "message_id": "m3", "text": "pricing"},
        {"contact_id": "demo-B", "message_id": "m1", "text": "pricing"},
        {"contact_id": "demo-A", "message_id": "m4", "text": "START"},
        {"contact_id": "demo-A", "message_id": "m5", "text": "book an appointment"},
        {"contact_id": "demo-A", "message_id": "m6", "text": "Where is my parcel?"},
    ]
    for event in events:
        print(json.dumps({"event": event, "decision": bot.handle(event)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="print a deterministic synthetic trace")
    args = parser.parse_args()
    if args.demo:
        demo()
