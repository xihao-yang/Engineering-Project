from __future__ import annotations

import csv
import io
import uuid
from pathlib import Path
from typing import Any

from app.config import Settings
from app.database import (
    cancel_receipt,
    confirm_receipt,
    create_receipt,
    get_receipt,
    get_stats,
    init_db,
    list_receipts_for_export,
    open_db,
    today_iso,
)
from app.models import OCRResult
from app.ocr import OCRProvider
from app.parser import parse_receipt_text


class ReceiptService:
    def __init__(self, settings: Settings, ocr_provider: OCRProvider) -> None:
        self.settings = settings
        self.ocr_provider = ocr_provider
        self.settings.upload_dir.mkdir(parents=True, exist_ok=True)
        with open_db(self.settings.db_path) as conn:
            init_db(conn)

    def scan_receipt(
        self,
        image_bytes: bytes,
        filename: str | None,
        timezone_name: str = "Asia/Tokyo",
        ocr_text_override: str | None = None,
    ) -> dict[str, Any]:
        receipt_id = uuid.uuid4().hex
        image_path = self._save_image(receipt_id, image_bytes, filename)

        if ocr_text_override:
            ocr_result = OCRResult(text=ocr_text_override, confidence=0.7)
        else:
            ocr_result = self.ocr_provider.extract_text(image_bytes, filename)

        candidate = parse_receipt_text(ocr_result.text)
        confidence = round(max(candidate.confidence, ocr_result.confidence), 2)
        needs_review = candidate.needs_review or not ocr_result.text.strip()

        receipt = {
            "id": receipt_id,
            "image_path": str(image_path),
            "store_name": candidate.store_name,
            "purchase_date": candidate.purchase_date or today_iso(),
            "total_amount": candidate.total_amount or 0,
            "payment_method": candidate.payment_method,
            "category": candidate.category,
            "ocr_text": candidate.ocr_text,
            "confidence": confidence,
            "status": "draft",
        }
        with open_db(self.settings.db_path) as conn:
            create_receipt(conn, receipt)

        warnings = list(candidate.warnings)
        if not ocr_result.text.strip():
            warnings.append("ocr_text_empty")

        return {
            "receipt_id": receipt_id,
            "store_name": candidate.store_name,
            "date": candidate.purchase_date,
            "total_amount": candidate.total_amount,
            "payment_method": candidate.payment_method,
            "category": candidate.category,
            "confidence": confidence,
            "needs_review": needs_review,
            "warnings": warnings,
            "timezone": timezone_name,
        }

    def confirm(self, receipt_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        normalized = {
            "store_name": values["store_name"].strip(),
            "purchase_date": values["date"],
            "total_amount": int(values["total_amount"]),
            "payment_method": values.get("payment_method"),
            "category": values.get("category") or "其他",
        }
        with open_db(self.settings.db_path) as conn:
            exists = get_receipt(conn, receipt_id)
            if not exists:
                return None
            confirm_receipt(conn, receipt_id, normalized)
            saved = get_receipt(conn, receipt_id)
        return saved

    def cancel(self, receipt_id: str) -> bool:
        with open_db(self.settings.db_path) as conn:
            return cancel_receipt(conn, receipt_id)

    def stats(self, range_name: str, group_by: str | None = None) -> dict[str, Any]:
        with open_db(self.settings.db_path) as conn:
            return get_stats(conn, range_name, group_by)

    def export_csv(self, range_name: str) -> str:
        with open_db(self.settings.db_path) as conn:
            rows = list_receipts_for_export(conn, range_name)

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["date", "store_name", "total_amount", "payment_method", "category", "created_at"],
        )
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()

    def _save_image(self, receipt_id: str, image_bytes: bytes, filename: str | None) -> Path:
        suffix = Path(filename or "").suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".heic", ".webp", ".txt"}:
            suffix = ".jpg"
        path = self.settings.upload_dir / f"{receipt_id}{suffix}"
        path.write_bytes(image_bytes)
        return path
