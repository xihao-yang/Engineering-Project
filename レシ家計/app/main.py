from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, Field

from app.config import get_settings
from app.ocr import build_ocr_provider
from app.services import ReceiptService


class ConfirmReceiptRequest(BaseModel):
    store_name: str = Field(min_length=1)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    total_amount: int = Field(gt=0)
    payment_method: str | None = None
    category: str = "其他"


@lru_cache(maxsize=1)
def get_service() -> ReceiptService:
    settings = get_settings()
    provider = build_ocr_provider(settings)
    return ReceiptService(settings, provider)


app = FastAPI(
    title="レシ家計 Receipt API",
    version="0.1.0",
    description="MVP backend for Japanese receipt recognition bookkeeping.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/receipts/scan")
async def scan_receipt(
    image: Annotated[UploadFile, File()],
    timezone: Annotated[str, Form()] = "Asia/Tokyo",
    ocr_text: Annotated[str | None, Form()] = None,
) -> dict:
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="image is required")
    return get_service().scan_receipt(
        image_bytes=image_bytes,
        filename=image.filename,
        timezone_name=timezone,
        ocr_text_override=ocr_text,
    )


@app.post("/api/receipts/{receipt_id}/confirm")
def confirm_receipt(receipt_id: str, request: ConfirmReceiptRequest) -> dict:
    saved = get_service().confirm(receipt_id, request.model_dump())
    if saved is None:
        raise HTTPException(status_code=404, detail="receipt not found")
    return {"ok": True, "receipt_id": receipt_id, "status": saved["status"]}


@app.post("/api/receipts/{receipt_id}/cancel")
def cancel_receipt(receipt_id: str) -> dict:
    ok = get_service().cancel(receipt_id)
    if not ok:
        raise HTTPException(status_code=404, detail="receipt not found")
    return {"ok": True, "receipt_id": receipt_id, "status": "cancelled"}


@app.get("/api/stats")
def stats(
    range: Annotated[str, Query(pattern="^(today|month|last_month)$")] = "month",
    group_by: Annotated[str | None, Query(pattern="^(category|store)$")] = None,
) -> dict:
    return get_service().stats(range, group_by)


@app.get("/api/receipts/export.csv", response_class=PlainTextResponse)
def export_receipts(
    range: Annotated[str, Query(pattern="^(today|month|last_month)$")] = "month",
) -> Response:
    csv_text = get_service().export_csv(range)
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="receipts-{range}.csv"'},
    )
