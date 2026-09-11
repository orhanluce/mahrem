"""Extract local documents into plain text, never copy source containers to output."""
from dataclasses import dataclass
from pathlib import Path
import re
from zipfile import ZipFile

from defusedxml import ElementTree
from pypdf import PdfReader

INPUT_SUFFIXES = {'.txt', '.md', '.docx', '.pdf'}
TEXT_SUFFIXES = {'.txt', '.md'}
MAX_EXPANDED_BYTES = 20_000_000
MAX_TEXT_CHARS = 2_000_000
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class DocumentError(ValueError):
    """A controlled message safe to return across the local tool boundary."""


@dataclass(frozen=True)
class DocumentText:
    text: str
    warnings: list[str]


def read_document(path: Path) -> DocumentText:
    suffix = path.suffix.lower()
    warnings: list[str] = []
    if suffix in TEXT_SUFFIXES:
        text = path.read_text(encoding='utf-8-sig')
    elif suffix == '.docx':
        text, warnings = _docx(path)
    elif suffix == '.pdf':
        text, warnings = _pdf(path)
    else:
        raise ValueError('Desteklenen biçimler: TXT, Markdown, DOCX ve metin içeren PDF.')
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError('Çıkarılan metin boyut sınırını aşıyor; belgeyi bölün.')
    if not text.strip():
        raise ValueError('Okunabilir metin bulunamadı. Taranmış belgeler için yerel OCR gerekir.')
    return DocumentText(text, warnings)


def _docx(path: Path) -> tuple[str, list[str]]:
    warnings = ['DOCX düz metne dönüştürüldü; biçim, resim, imza ve belge özellikleri çıktıya taşınmaz.']
    try:
        with ZipFile(path) as archive:
            if sum(info.file_size for info in archive.infolist()) > MAX_EXPANDED_BYTES:
                raise DocumentError('DOCX açılmış boyut sınırını aşıyor.')
            names = archive.namelist()
            if 'word/document.xml' not in names:
                raise DocumentError('Geçerli bir Word DOCX belgesi değil.')
            parts = ['word/document.xml'] + sorted(
                name for name in names if re.fullmatch(
                    r'word/(?:header\d+|footer\d+|footnotes|endnotes|comments)\.xml', name
                )
            )
            chunks = []
            for part in parts:
                root = ElementTree.fromstring(archive.read(part))
                paragraphs = []
                for paragraph in root.iter(W + 'p'):
                    # Runs are joined before detection: split-run email/IDs stay detectable.
                    pieces = []
                    for node in paragraph.iter():
                        if node.tag in {W + 't', W + 'delText'}:
                            pieces.append(node.text or '')
                        elif node.tag == W + 'tab':
                            pieces.append('\t')
                        elif node.tag in {W + 'br', W + 'cr'}:
                            pieces.append('\n')
                    paragraphs.append(''.join(pieces))
                chunks.append('\n'.join(paragraphs))
            if any(name.startswith(('word/media/', 'word/embeddings/')) for name in names):
                warnings.append('Görsel veya gömülü dosya var; bunların içindeki yazılar okunmadı. Yerelde kontrol edin.')
            return '\n\n'.join(chunks), warnings
    except DocumentError:
        raise
    except Exception:
        raise ValueError('DOCX açılamadı; dosya bozuk, şifreli veya farklı bir biçimde olabilir.') from None


def _pdf(path: Path) -> tuple[str, list[str]]:
    warnings = ['PDF düz metne dönüştürüldü; sayfa düzeni ve imza korunmaz. Orijinal PDF karartılmaz.']
    try:
        reader = PdfReader(path)
        if reader.is_encrypted:
            raise DocumentError('Şifreli PDF desteklenmiyor; şifreyi sohbete göndermeyin.')
        if len(reader.pages) > 250:
            raise DocumentError('PDF en fazla 250 sayfa olabilir; belgeyi bölün.')
        chunks = []
        for index, page in enumerate(reader.pages, 1):
            contents = page.get_contents()
            if contents is not None and len(contents.get_data()) > MAX_EXPANDED_BYTES:
                raise DocumentError('PDF sayfası açılmış boyut sınırını aşıyor.')
            text = page.extract_text() or ''
            if not text.strip():
                raise DocumentError(f'PDF sayfa {index} okunabilir metin içermiyor; yerel OCR veya boş sayfanın çıkarılması gerekir.')
            chunks.append(text)
            if sum(map(len, chunks)) > MAX_TEXT_CHARS:
                raise DocumentError('PDF metni boyut sınırını aşıyor.')
        warnings.append('Görsel yazıları, form alanları ve ekler aktarılmaz; metin sırasını ve eksikleri yerelde kontrol edin.')
        return '\n\n'.join(chunks), warnings
    except DocumentError:
        raise
    except Exception:
        # Parser exceptions can contain snippets from an untrusted document.
        raise ValueError('PDF okunamadı; geçerli, şifresiz ve metin içeren bir PDF kullanın.') from None
