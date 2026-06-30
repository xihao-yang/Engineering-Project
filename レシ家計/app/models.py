from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float = 0.0


@dataclass(frozen=True)
class ReceiptCandidate:
    store_name: str | None
    purchase_date: str | None
    total_amount: int | None
    payment_method: str | None
    category: str
    ocr_text: str
    confidence: float
    needs_review: bool
    warnings: list[str] = field(default_factory=list)
