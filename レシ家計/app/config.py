from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    db_path: Path
    upload_dir: Path
    ocr_provider: str
    openai_api_key: str | None
    openai_model: str


def _path_from_env(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def get_settings() -> Settings:
    return Settings(
        db_path=_path_from_env("RECEIPT_DB_PATH", "data/receipts.sqlite3"),
        upload_dir=_path_from_env("RECEIPT_UPLOAD_DIR", "data/uploads"),
        ocr_provider=os.getenv("RECEIPT_OCR_PROVIDER", "mock").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
    )
