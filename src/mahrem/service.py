from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

from .detectors import find_candidates, load_rules
from .masking import MaskSession, normalize_label


ALLOWED_SUFFIXES = {".txt", ".md"}


class LocalPrivacyService:
    def __init__(self, max_file_bytes: int | None = None) -> None:
        configured = os.environ.get("MAHREM_MAX_FILE_BYTES", "2000000")
        self.max_file_bytes = max_file_bytes if max_file_bytes is not None else int(configured)
        self._sessions: dict[str, MaskSession] = {}

    def _input_path(self, raw_path: str, allowed_suffixes: set[str] | None = None) -> Path:
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            raise ValueError("Guvenli ve acik bir sinir icin mutlak dosya yolu kullanin.")
        path = path.resolve(strict=True)
        if not path.is_file():
            raise ValueError("Kaynak yolu bir dosya olmali.")
        suffixes = allowed_suffixes or ALLOWED_SUFFIXES
        if path.suffix.lower() not in suffixes:
            raise ValueError(f"Desteklenmeyen dosya turu: {path.suffix or '(uzantisiz)'}")
        if path.stat().st_size > self.max_file_bytes:
            raise ValueError(f"Dosya {self.max_file_bytes} baytlik guvenlik sinirini asiyor.")
        return path

    @staticmethod
    def _output_path(source: Path, raw_path: str, marker: str) -> Path:
        if raw_path:
            path = Path(raw_path).expanduser()
            if not path.is_absolute():
                raise ValueError("Cikti yolu veriliyorsa mutlak olmali.")
            path = path.resolve(strict=False)
        else:
            stem = source.stem
            if marker == "restored" and stem.endswith(".masked"):
                stem = stem[: -len(".masked")]
            path = source.with_name(f"{stem}.{marker}{source.suffix}")
        if path == source:
            raise ValueError("Kaynak dosyanin uzerine yazilamaz.")
        if not path.parent.is_dir():
            raise ValueError("Cikti klasoru mevcut degil.")
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError("Cikti uzantisi .txt veya .md olmali.")
        return path

    def _rules(self, raw_path: str) -> dict[str, object]:
        if not raw_path:
            return {}
        path = self._input_path(raw_path, {".json"})
        return load_rules(path)

    @staticmethod
    def _write(path: Path, content: str, overwrite: bool) -> None:
        mode = "w" if overwrite else "x"
        with path.open(mode, encoding="utf-8", newline="") as handle:
            handle.write(content)

    def scan_file(self, source_path: str, rules_path: str = "") -> dict[str, object]:
        source = self._input_path(source_path)
        text = source.read_text(encoding="utf-8")
        candidates = find_candidates(text, self._rules(rules_path))
        counts = Counter(normalize_label(item.category) for item in candidates)
        return {
            "source_path": str(source),
            "counts": dict(sorted(counts.items())),
            "detection_count": len(candidates),
            "raw_values_returned": False,
        }

    def mask_file(
        self,
        source_path: str,
        rules_path: str = "",
        output_path: str = "",
        overwrite: bool = False,
    ) -> dict[str, object]:
        source = self._input_path(source_path)
        target = self._output_path(source, output_path, "masked")
        text = source.read_text(encoding="utf-8")
        session = MaskSession()
        result = session.mask(text, self._rules(rules_path))
        self._write(target, result.masked_text, overwrite)
        self._sessions[session.session_id] = session
        return {
            "session_id": session.session_id,
            "masked_path": str(target),
            "masked_text": result.masked_text,
            "counts": result.counts,
            "replacement_count": result.replacement_count,
            "mapping_storage": "memory_only",
        }

    def restore_file(
        self,
        masked_path: str,
        session_id: str,
        output_path: str = "",
        overwrite: bool = False,
    ) -> dict[str, object]:
        source = self._input_path(masked_path)
        target = self._output_path(source, output_path, "restored")
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError("Oturum bulunamadi veya MCP sureci yeniden basladi.")
        restored, replaced, unknown = session.restore(source.read_text(encoding="utf-8"))
        self._write(target, restored, overwrite)
        return {
            "session_id": session_id,
            "restored_path": str(target),
            "replaced_token_count": replaced,
            "unknown_token_count": unknown,
            "restored_text_returned": False,
        }

    def forget_session(self, session_id: str) -> dict[str, object]:
        session = self._sessions.pop(session_id, None)
        return {
            "session_id": session_id,
            "forgotten": session is not None,
            "forgotten_token_count": session.token_count if session is not None else 0,
        }
