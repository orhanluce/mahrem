from __future__ import annotations

import re
import secrets
from collections import Counter
from dataclasses import dataclass, field

from .detectors import Candidate, find_candidates


TOKEN_PATTERN = re.compile(r"\[[A-Z0-9_-]+-\d+\]")
TRANSLATION = str.maketrans({"Ç": "C", "Ğ": "G", "İ": "I", "Ö": "O", "Ş": "S", "Ü": "U"})


def normalize_label(label: str) -> str:
    normalized = label.strip().upper().translate(TRANSLATION)
    normalized = re.sub(r"[^A-Z0-9_-]+", "_", normalized).strip("_")
    return normalized or "OZEL"


@dataclass(frozen=True, slots=True)
class MaskResult:
    masked_text: str
    counts: dict[str, int]
    replacement_count: int


@dataclass(slots=True)
class MaskSession:
    session_id: str = field(default_factory=lambda: secrets.token_urlsafe(12))
    _original_to_token: dict[tuple[str, str], str] = field(default_factory=dict)
    _token_to_original: dict[str, str] = field(default_factory=dict)
    _counters: Counter[str] = field(default_factory=Counter)

    def _token_for(self, candidate: Candidate) -> str:
        category = normalize_label(candidate.category)
        key = (category, candidate.value)
        existing = self._original_to_token.get(key)
        if existing is not None:
            return existing
        self._counters[category] += 1
        token = f"[{category}-{self._counters[category]}]"
        self._original_to_token[key] = token
        self._token_to_original[token] = candidate.value
        return token

    def mask(self, text: str, rules: dict[str, object] | None = None) -> MaskResult:
        candidates = find_candidates(text, rules)
        counts: Counter[str] = Counter()
        pieces: list[str] = []
        cursor = 0
        for candidate in candidates:
            pieces.append(text[cursor:candidate.start])
            token = self._token_for(candidate)
            pieces.append(token)
            counts[normalize_label(candidate.category)] += 1
            cursor = candidate.end
        pieces.append(text[cursor:])
        return MaskResult("".join(pieces), dict(sorted(counts.items())), len(candidates))

    def restore(self, text: str) -> tuple[str, int, int]:
        replaced = 0
        unknown = 0

        def replace(match: re.Match[str]) -> str:
            nonlocal replaced, unknown
            token = match.group(0)
            original = self._token_to_original.get(token)
            if original is None:
                unknown += 1
                return token
            replaced += 1
            return original

        return TOKEN_PATTERN.sub(replace, text), replaced, unknown

    @property
    def token_count(self) -> int:
        return len(self._token_to_original)
