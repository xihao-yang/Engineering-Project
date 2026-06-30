from __future__ import annotations

import re
from datetime import date

from app.classifier import classify_store
from app.models import ReceiptCandidate


DATE_PATTERNS = [
    re.compile(r"(?P<year>20\d{2})[./\-年](?P<month>\d{1,2})[./\-月](?P<day>\d{1,2})日?"),
    re.compile(r"(?P<year>\d{2})[./\-](?P<month>\d{1,2})[./\-](?P<day>\d{1,2})"),
]

TOTAL_KEYWORDS = [
    "合計",
    "総合計",
    "税込合計",
    "お支払い",
    "お支払",
    "支払金額",
    "合計金額",
    "お買上げ計",
]

AMOUNT_EXCLUDE_KEYWORDS = [
    "小計",
    "税",
    "内税",
    "外税",
    "対象",
    "お預り",
    "お預かり",
    "預り",
    "お釣り",
    "おつり",
    "釣銭",
]

STORE_EXCLUDE_KEYWORDS = [
    "領収書",
    "レシート",
    "receipt",
    "合計",
    "小計",
    "税",
    "お預り",
    "お釣り",
    "電話",
    "tel",
]

PAYMENT_KEYWORDS = [
    ("PayPay", ["paypay", "ペイペイ"]),
    ("交通系IC", ["交通系ic", "suica", "pasmo", "ic"]),
    ("クレジットカード", ["クレジット", "credit", "visa", "mastercard", "master", "jcb"]),
    ("現金", ["現金", "cash"]),
]


def parse_receipt_text(text: str) -> ReceiptCandidate:
    normalized = _normalize_text(text)
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]

    store_name = _parse_store_name(lines)
    purchase_date = _parse_date(normalized)
    total_amount = _parse_total_amount(lines)
    payment_method = _parse_payment_method(normalized)
    category = classify_store(store_name, normalized)

    warnings: list[str] = []
    if not store_name:
        warnings.append("store_name_not_found")
    if not purchase_date:
        warnings.append("purchase_date_not_found")
    if total_amount is None:
        warnings.append("total_amount_not_found")

    confidence = _score_candidate(store_name, purchase_date, total_amount, payment_method)
    needs_review = bool(warnings) or confidence < 0.75

    return ReceiptCandidate(
        store_name=store_name,
        purchase_date=purchase_date,
        total_amount=total_amount,
        payment_method=payment_method,
        category=category,
        ocr_text=normalized,
        confidence=confidence,
        needs_review=needs_review,
        warnings=warnings,
    )


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("￥", "¥")
    return "\n".join(line.strip() for line in text.splitlines())


def _parse_date(text: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        year = int(match.group("year"))
        if year < 100:
            year += 2000
        month = int(match.group("month"))
        day = int(match.group("day"))
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            continue
    return None


def _parse_store_name(lines: list[str]) -> str | None:
    for line in lines[:8]:
        lowered = line.lower()
        if any(keyword.lower() in lowered for keyword in STORE_EXCLUDE_KEYWORDS):
            continue
        if _find_amounts(line):
            continue
        if _parse_date(line):
            continue
        cleaned = _clean_store_name(line)
        if 2 <= len(cleaned) <= 60:
            return cleaned
    return None


def _clean_store_name(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip(" -:：")


def _parse_total_amount(lines: list[str]) -> int | None:
    candidates: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        is_total_line = any(keyword in line for keyword in TOTAL_KEYWORDS)
        if is_total_line and _is_payment_adjustment_line(line):
            continue
        if is_total_line:
            amounts = _find_amounts(line)
            for amount in amounts:
                candidates.append((index, amount))

    if candidates:
        # Later total lines are often closer to the final payable amount.
        return sorted(candidates, key=lambda item: (item[0], item[1]))[-1][1]

    fallback_amounts: list[int] = []
    for line in lines:
        if _is_excluded_amount_line(line):
            continue
        if _parse_date(line):
            continue
        fallback_amounts.extend(_find_amounts(line))

    if not fallback_amounts:
        return None
    return max(fallback_amounts)


def _is_excluded_amount_line(line: str) -> bool:
    return any(keyword in line for keyword in AMOUNT_EXCLUDE_KEYWORDS)


def _is_payment_adjustment_line(line: str) -> bool:
    adjustment_keywords = ["お預り", "お預かり", "預り", "お釣り", "おつり", "釣銭"]
    return any(keyword in line for keyword in adjustment_keywords)


def _find_amounts(line: str) -> list[int]:
    amounts: list[int] = []
    for match in re.finditer(r"(?:¥\s*)?(\d{1,3}(?:,\d{3})+|\d{2,6})\s*(?:円)?", line):
        raw = match.group(1).replace(",", "")
        try:
            value = int(raw)
        except ValueError:
            continue
        if 10 <= value <= 10_000_000:
            amounts.append(value)
    return amounts


def _parse_payment_method(text: str) -> str | None:
    lowered = text.lower()
    for normalized, keywords in PAYMENT_KEYWORDS:
        if any(keyword.lower() in lowered for keyword in keywords):
            return normalized
    return None


def _score_candidate(
    store_name: str | None,
    purchase_date: str | None,
    total_amount: int | None,
    payment_method: str | None,
) -> float:
    score = 0.0
    if store_name:
        score += 0.25
    if purchase_date:
        score += 0.25
    if total_amount is not None and total_amount > 0:
        score += 0.35
    if payment_method:
        score += 0.15
    return round(score, 2)
