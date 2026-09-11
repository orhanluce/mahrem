from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


Validator = Callable[[str], bool]


@dataclass(frozen=True, slots=True)
class Candidate:
    start: int
    end: int
    category: str
    value: str
    priority: int


@dataclass(frozen=True, slots=True)
class Detector:
    category: str
    pattern: re.Pattern[str]
    priority: int
    validator: Validator | None = None


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def validate_tckn(value: str) -> bool:
    digits = _digits(value)
    if len(digits) != 11 or digits[0] == "0" or len(set(digits)) == 1:
        return False
    numbers = [int(char) for char in digits]
    tenth = ((sum(numbers[0:9:2]) * 7) - sum(numbers[1:8:2])) % 10
    eleventh = sum(numbers[:10]) % 10
    return numbers[9] == tenth and numbers[10] == eleventh


def validate_iban(value: str) -> bool:
    compact = re.sub(r"[\s-]", "", value).upper()
    if not re.fullmatch(r"TR\d{24}", compact):
        return False
    rearranged = compact[4:] + compact[:4]
    numeric = "".join(str(ord(char) - 55) if char.isalpha() else char for char in rearranged)
    return int(numeric) % 97 == 1


def validate_luhn(value: str) -> bool:
    digits = _digits(value)
    if not 13 <= len(digits) <= 19 or len(set(digits)) == 1:
        return False
    total = 0
    parity = len(digits) % 2
    for index, char in enumerate(digits):
        number = int(char)
        if index % 2 == parity:
            number *= 2
            if number > 9:
                number -= 9
        total += number
    return total % 10 == 0


def validate_phone(value: str) -> bool:
    digits = _digits(value)
    if digits.startswith("90"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = digits[1:]
    return len(digits) == 10 and digits[0] == "5"


def validate_ipv4(value: str) -> bool:
    try:
        octets = [int(part) for part in value.split(".")]
    except ValueError:
        return False
    return len(octets) == 4 and all(0 <= part <= 255 for part in octets)


DETECTORS = (
    Detector(
        "EPOSTA",
        re.compile(r"(?<![\w.+-])[\w.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"),
        100,
    ),
    Detector("TCKN", re.compile(r"(?<!\d)[1-9]\d{10}(?!\d)"), 95, validate_tckn),
    Detector("IBAN", re.compile(r"(?i)(?<![A-Z0-9])TR(?:[ -]?\d){24}(?![A-Z0-9])"), 90, validate_iban),
    Detector("KART", re.compile(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)"), 85, validate_luhn),
    Detector(
        "TELEFON",
        re.compile(r"(?<!\d)(?:\+?90[\s().-]*)?(?:0[\s().-]*)?5\d{2}[\s().-]*\d{3}[\s.-]*\d{2}[\s.-]*\d{2}(?!\d)"),
        80,
        validate_phone,
    ),
    Detector("URL", re.compile(r"(?i)\bhttps?://[^\s<>()]+"), 120),
    Detector("IP", re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"), 70, validate_ipv4),
)


ROLE_NAME_PATTERN = re.compile(
    r"(?i:\b(?:davac[ıi]|daval[ıi]|m[üu]vekkil|vekil|hasta|m[üu][şs]teri|ad[ıi ]*soyad[ıi]?))[ \t]*[:\-][ \t]*"
    r"([A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü]+(?:[ \t]+[A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü]+){1,3})"
)


def load_rules(path: Path | None) -> dict[str, object]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Kural dosyasinin kok degeri JSON nesnesi olmali.")
    literal_terms = data.get("literal_terms", [])
    allowlist = data.get("allowlist", [])
    if not isinstance(literal_terms, list) or not isinstance(allowlist, list):
        raise ValueError("literal_terms ve allowlist dizi olmali.")
    for item in literal_terms:
        if not isinstance(item, dict) or not isinstance(item.get("value"), str):
            raise ValueError("Her literal_terms kaydi value alanina sahip olmali.")
        if "label" in item and not isinstance(item["label"], str):
            raise ValueError("literal_terms label alani metin olmali.")
    if not all(isinstance(item, str) for item in allowlist):
        raise ValueError("allowlist yalnizca metin degerleri icermeli.")
    return data


def find_candidates(text: str, rules: dict[str, object] | None = None) -> list[Candidate]:
    rules = rules or {}
    allowlist = {item.casefold() for item in rules.get("allowlist", []) if isinstance(item, str)}
    candidates: list[Candidate] = []

    for detector in DETECTORS:
        for match in detector.pattern.finditer(text):
            value = match.group(0)
            if value.casefold() in allowlist:
                continue
            if detector.validator is not None and not detector.validator(value):
                continue
            candidates.append(Candidate(match.start(), match.end(), detector.category, value, detector.priority))

    for match in ROLE_NAME_PATTERN.finditer(text):
        value = match.group(1)
        if value.casefold() not in allowlist:
            candidates.append(Candidate(match.start(1), match.end(1), "KISI", value, 60))

    literal_terms = rules.get("literal_terms", [])
    if isinstance(literal_terms, list):
        for item in literal_terms:
            if not isinstance(item, dict):
                continue
            value = item.get("value")
            if not isinstance(value, str) or not value or value.casefold() in allowlist:
                continue
            category = item.get("label", "OZEL")
            if not isinstance(category, str):
                category = "OZEL"
            for match in re.finditer(re.escape(value), text, flags=re.IGNORECASE):
                candidates.append(Candidate(match.start(), match.end(), category, match.group(0), 110))

    selected: list[Candidate] = []
    for candidate in sorted(candidates, key=lambda item: (-item.priority, -(item.end - item.start), item.start)):
        if any(candidate.start < kept.end and kept.start < candidate.end for kept in selected):
            continue
        selected.append(candidate)
    return sorted(selected, key=lambda item: item.start)
