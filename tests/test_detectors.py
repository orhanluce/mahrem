from __future__ import annotations

import unittest

from mahrem.detectors import find_candidates, validate_iban, validate_luhn, validate_tckn


class DetectorTests(unittest.TestCase):
    def test_tckn_checksum(self) -> None:
        self.assertTrue(validate_tckn("10000000146"))
        self.assertFalse(validate_tckn("10000000145"))
        self.assertFalse(validate_tckn("11111111111"))

    def test_iban_mod97(self) -> None:
        self.assertTrue(validate_iban("TR78 9999 9999 9999 9999 9999 99"))
        self.assertFalse(validate_iban("TR00 9999 9999 9999 9999 9999 99"))

    def test_luhn(self) -> None:
        self.assertTrue(validate_luhn("4111 1111 1111 1111"))
        self.assertFalse(validate_luhn("4111 1111 1111 1112"))

    def test_structured_and_contextual_detections(self) -> None:
        text = (
            "Musteri: Ayse Deneme\n"
            "TCKN: 10000000146\n"
            "Telefon: +90 555 000 11 22\n"
            "E-posta: ayse.deneme@example.com\n"
            "IP: 192.0.2.10"
        )
        categories = {candidate.category for candidate in find_candidates(text)}
        self.assertEqual(categories, {"KISI", "TCKN", "TELEFON", "EPOSTA", "IP"})

    def test_invalid_identifiers_are_not_masked(self) -> None:
        categories = {candidate.category for candidate in find_candidates("TCKN 10000000145, IP 999.2.3.4")}
        self.assertNotIn("TCKN", categories)
        self.assertNotIn("IP", categories)

    def test_local_literal_rule_and_allowlist(self) -> None:
        rules = {
            "literal_terms": [{"value": "Ozel Musteri A.S.", "label": "KURUM"}],
            "allowlist": ["192.0.2.10"],
        }
        candidates = find_candidates("Ozel Musteri A.S. 192.0.2.10", rules)
        self.assertEqual([(item.category, item.value) for item in candidates], [("KURUM", "Ozel Musteri A.S.")])


if __name__ == "__main__":
    unittest.main()
