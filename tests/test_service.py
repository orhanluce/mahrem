from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mahrem.service import LocalPrivacyService


class ServiceTests(unittest.TestCase):
    def test_scan_does_not_return_raw_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory, "source.txt")
            source.write_text("E-posta: private@example.com", encoding="utf-8")
            result = LocalPrivacyService().scan_file(str(source))

        serialized = json.dumps(result)
        self.assertNotIn("private@example.com", serialized)
        self.assertEqual(result["counts"], {"EPOSTA": 1})
        self.assertFalse(result["raw_values_returned"])

    def test_mask_edit_restore_flow_never_returns_clear_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory, "source.md")
            source.write_text("Kisi: private@example.com", encoding="utf-8")
            service = LocalPrivacyService()

            masked = service.mask_file(str(source))
            masked_path = Path(str(masked["masked_path"]))
            self.assertEqual(masked_path.read_text(encoding="utf-8"), "Kisi: [EPOSTA-1]")

            masked_path.write_text("Duzenlendi: [EPOSTA-1]", encoding="utf-8")
            restored = service.restore_file(str(masked_path), str(masked["session_id"]))
            restored_path = Path(str(restored["restored_path"]))

            self.assertEqual(restored_path.read_text(encoding="utf-8"), "Duzenlendi: private@example.com")
            self.assertNotIn("private@example.com", json.dumps(restored))
            self.assertFalse(restored["restored_text_returned"])

    def test_session_can_be_forgotten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory, "source.txt")
            source.write_text("private@example.com", encoding="utf-8")
            service = LocalPrivacyService()
            masked = service.mask_file(str(source))
            result = service.forget_session(str(masked["session_id"]))
            self.assertTrue(result["forgotten"])
            with self.assertRaisesRegex(ValueError, "Oturum bulunamadi"):
                service.restore_file(str(masked["masked_path"]), str(masked["session_id"]))

    def test_relative_paths_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "mutlak"):
            LocalPrivacyService().scan_file("source.txt")

    def test_existing_output_is_not_overwritten_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory, "source.txt")
            source.write_text("private@example.com", encoding="utf-8")
            target = Path(directory, "source.masked.txt")
            target.write_text("kullanici verisi", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                LocalPrivacyService().mask_file(str(source))
            self.assertEqual(target.read_text(encoding="utf-8"), "kullanici verisi")


if __name__ == "__main__":
    unittest.main()
