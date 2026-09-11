import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

from mahrem.service import LocalPrivacyService
from mahrem.masking import MaskSession


def write_pdf(path, texts):
    writer = PdfWriter()
    for text in texts:
        page = writer.add_blank_page(width=612, height=792)
        if not text:
            continue
        font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                 NameObject('/Subtype'): NameObject('/Type1'),
                                 NameObject('/BaseFont'): NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({
            NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
        stream = DecodedStreamObject()
        stream.set_data(f'BT /F1 12 Tf 40 700 Td ({text}) Tj ET'.encode('ascii'))
        page[NameObject('/Contents')] = stream
    with path.open('wb') as output:
        writer.write(output)


class DocumentTests(unittest.TestCase):
    def test_parser_errors_do_not_return_document_snippets(self):
        with tempfile.TemporaryDirectory() as folder:
            for suffix, parser in [('pdf', 'mahrem.documents.PdfReader'),
                                   ('docx', 'mahrem.documents.ZipFile')]:
                path = Path(folder, 'source.' + suffix)
                path.write_bytes(b'synthetic fixture')
                with patch(parser, side_effect=ValueError('private@example.com')):
                    with self.assertRaises(ValueError) as caught:
                        LocalPrivacyService().mask_file(str(path))
                self.assertNotIn('private@example.com', str(caught.exception))
                self.assertFalse(path.with_suffix('.masked.txt').exists())

    def test_docx_runs_tables_header_and_no_container_leak(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, 'source.docx')
            with ZipFile(path, 'w') as archive:
                archive.writestr('word/document.xml', '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
                <w:p><w:r><w:t>private@</w:t></w:r><w:r><w:t>example.com</w:t></w:r></w:p>
                <w:tbl><w:tr><w:tc><w:p><w:r><w:t>10000000146</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
                </w:body></w:document>''')
                archive.writestr('word/header1.xml', '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>header@example.com</w:t></w:r></w:p></w:hdr>')
                archive.writestr('docProps/core.xml', 'metadata-secret')
            original = path.read_bytes()
            service = LocalPrivacyService()
            result = service.mask_file(str(path))
            self.assertEqual(result['counts'], {'EPOSTA': 2, 'TCKN': 1})
            self.assertTrue(result['masked_path'].endswith('.masked.txt'))
            self.assertNotIn('private@example.com', json.dumps(result))
            self.assertNotIn('metadata-secret', result['masked_text'])
            self.assertEqual(path.read_bytes(), original)
            restored = service.restore_file(result['masked_path'], result['session_id'])
            self.assertIn('private@example.com', Path(restored['restored_path']).read_text())
            self.assertNotIn('private@example.com', json.dumps(restored))

    def test_pdf_to_masked_text_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, 'source.pdf')
            write_pdf(path, ['private@example.com', '10000000146'])
            original = path.read_bytes()
            service = LocalPrivacyService()
            result = service.mask_file(str(path))
            self.assertEqual(result['counts'], {'EPOSTA': 1, 'TCKN': 1})
            self.assertNotIn('private@example.com', json.dumps(result))
            restored = service.restore_file(result['masked_path'], result['session_id'])
            self.assertIn('private@example.com', Path(restored['restored_path']).read_text())
            self.assertEqual(path.read_bytes(), original)

    def test_mixed_pdf_with_unreadable_page_fails_without_output(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, 'mixed.pdf')
            write_pdf(path, ['readable@example.com', ''])
            with self.assertRaisesRegex(ValueError, 'sayfa 2'):
                LocalPrivacyService().mask_file(str(path))
            self.assertFalse(path.with_suffix('.masked.txt').exists())

    def test_encrypted_pdf_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, 'locked.pdf')
            writer = PdfWriter()
            writer.add_blank_page(200, 200)
            writer.encrypt('test-only')
            with path.open('wb') as output:
                writer.write(output)
            with self.assertRaisesRegex(ValueError, 'Şifreli'):
                LocalPrivacyService().mask_file(str(path))

    def test_output_pdf_is_rejected_not_fake_text_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, 'source.txt')
            path.write_text('private@example.com')
            with self.assertRaises(ValueError):
                LocalPrivacyService().mask_file(str(path), output_path=str(Path(folder,'out.pdf')))

    def test_placeholder_collision_rejected(self):
        with self.assertRaises(ValueError):
            MaskSession().mask('[EPOSTA-1] and private@example.com')

    def test_names_do_not_consume_next_line(self):
        result = MaskSession().mask('Müşteri: Ayşe Deneme\nTelefon: +90 555 000 11 22')
        self.assertIn('Müşteri: [KISI-1]\nTelefon:', result.masked_text)

    def test_hyphen_iban_and_url_with_email(self):
        result = MaskSession().mask('TR78-9999-9999-9999-9999-9999-99 https://example.com/?email=x@example.com&secret=yes')
        self.assertEqual(result.masked_text, '[IBAN-1] [URL-1]')
