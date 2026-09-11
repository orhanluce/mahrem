from __future__ import annotations

import unittest

from mahrem.masking import MaskSession


class MaskSessionTests(unittest.TestCase):
    def test_repeated_value_gets_same_token_and_round_trips(self) -> None:
        original = "Yaz: kisi@example.com. Tekrar: kisi@example.com."
        session = MaskSession(session_id="test-session")
        result = session.mask(original)

        self.assertEqual(result.masked_text.count("[EPOSTA-1]"), 2)
        self.assertNotIn("kisi@example.com", result.masked_text)
        restored, replaced, unknown = session.restore(result.masked_text)
        self.assertEqual(restored, original)
        self.assertEqual(replaced, 2)
        self.assertEqual(unknown, 0)

    def test_unknown_placeholder_is_preserved(self) -> None:
        session = MaskSession(session_id="test-session")
        restored, replaced, unknown = session.restore("[KISI-99]")
        self.assertEqual(restored, "[KISI-99]")
        self.assertEqual(replaced, 0)
        self.assertEqual(unknown, 1)


if __name__ == "__main__":
    unittest.main()
