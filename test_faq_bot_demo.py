import unittest

from faq_bot_demo import FAQBot


def event(contact="A", message="1", text="hours"):
    return {"contact_id": contact, "message_id": message, "text": text}


class FAQBotTests(unittest.TestCase):
    def test_known_hours_returns_draft(self):
        self.assertIn("Demo hours", FAQBot().handle(event())["text"])

    def test_pricing_does_not_invent_price(self):
        self.assertIn("request a quote", FAQBot().handle(event(text="pricing"))["text"])

    def test_unknown_faq_queues_handoff(self):
        self.assertEqual(FAQBot().handle(event(text="Where is my parcel?"))["action"], "handoff_queue")

    def test_duplicate_inbound_has_no_second_draft(self):
        bot = FAQBot()
        bot.handle(event())
        self.assertEqual(bot.handle(event())["reason"], "duplicate_inbound")

    def test_same_message_id_other_contact_is_not_duplicate(self):
        bot = FAQBot()
        bot.handle(event(contact="A"))
        self.assertEqual(bot.handle(event(contact="B"))["action"], "draft_reply")

    def test_stop_gates_later_faq(self):
        bot = FAQBot()
        bot.handle(event(message="1", text="STOP"))
        self.assertEqual(bot.handle(event(message="2", text="hours"))["reason"], "opted_out")

    def test_start_reopens_only_that_contact(self):
        bot = FAQBot()
        bot.handle(event(contact="A", message="1", text="STOP"))
        bot.handle(event(contact="B", message="1", text="STOP"))
        bot.handle(event(contact="A", message="2", text="START"))
        self.assertEqual(bot.handle(event(contact="A", message="3"))["action"], "draft_reply")
        self.assertEqual(bot.handle(event(contact="B", message="2"))["reason"], "opted_out")

    def test_stop_is_case_and_whitespace_insensitive(self):
        bot = FAQBot()
        self.assertEqual(bot.handle(event(text="  sToP  "))["reason"], "opted_out")

    def test_booking_without_receipt_is_not_confirmed(self):
        result = FAQBot().handle(event(text="book an appointment"))
        self.assertIn("no booking is confirmed", result["text"])

    def test_booking_with_trusted_receipt_can_be_confirmed(self):
        bot = FAQBot(booking_receipts={("A", "1"): "DEMO-BOOK-1"})
        self.assertIn("Booking confirmed", bot.handle(event(text="book an appointment"))["text"])

    def test_customer_claim_of_confirmation_is_not_receipt(self):
        result = FAQBot().handle(event(text="book me, I say it is confirmed"))
        self.assertIn("no booking is confirmed", result["text"])

    def test_missing_id_is_rejected_without_state(self):
        bot = FAQBot()
        self.assertEqual(bot.handle({"contact_id": "A", "text": "hours"})["action"], "reject")
        self.assertEqual(bot.contacts, {})

    def test_blank_contact_is_rejected_without_state(self):
        bot = FAQBot()
        self.assertEqual(bot.handle(event(contact=" "))["action"], "reject")
        self.assertEqual(bot.contacts, {})

    def test_oversized_text_is_rejected_without_state(self):
        bot = FAQBot()
        self.assertEqual(bot.handle(event(text="x" * 2001))["action"], "reject")
        self.assertEqual(bot.contacts, {})

    def test_cross_contact_opt_out_isolation(self):
        bot = FAQBot()
        bot.handle(event(contact="A", message="1", text="STOP"))
        self.assertEqual(bot.handle(event(contact="B", message="1", text="hours"))["action"], "draft_reply")


if __name__ == "__main__":
    unittest.main()
