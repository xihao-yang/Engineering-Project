from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from collections.abc import Iterator
from typing import Any


JST = timezone(timedelta(hours=9))


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def open_db(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS receipts (
          id TEXT PRIMARY KEY,
          image_path TEXT,
          store_name TEXT,
          purchase_date TEXT NOT NULL,
          total_amount INTEGER NOT NULL DEFAULT 0,
          payment_method TEXT,
          category TEXT,
          ocr_text TEXT,
          confidence REAL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_receipts_status_date ON receipts(status, purchase_date);"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_receipts_category ON receipts(category);"
    )
    conn.commit()


def now_iso() -> str:
    return datetime.now(tz=JST).isoformat(timespec="seconds")


def today_iso() -> str:
    return datetime.now(tz=JST).date().isoformat()


def create_receipt(conn: sqlite3.Connection, receipt: dict[str, Any]) -> None:
    timestamp = now_iso()
    conn.execute(
        """
        INSERT INTO receipts (
          id, image_path, store_name, purchase_date, total_amount,
          payment_method, category, ocr_text, confidence, status,
          created_at, updated_at
        )
        VALUES (
          :id, :image_path, :store_name, :purchase_date, :total_amount,
          :payment_method, :category, :ocr_text, :confidence, :status,
          :created_at, :updated_at
        );
        """,
        {
            **receipt,
            "created_at": receipt.get("created_at", timestamp),
            "updated_at": receipt.get("updated_at", timestamp),
        },
    )
    conn.commit()


def get_receipt(conn: sqlite3.Connection, receipt_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM receipts WHERE id = ?;", (receipt_id,)).fetchone()
    if row is None:
        return None
    return dict(row)


def confirm_receipt(conn: sqlite3.Connection, receipt_id: str, values: dict[str, Any]) -> bool:
    result = conn.execute(
        """
        UPDATE receipts
        SET store_name = :store_name,
            purchase_date = :purchase_date,
            total_amount = :total_amount,
            payment_method = :payment_method,
            category = :category,
            status = 'confirmed',
            updated_at = :updated_at
        WHERE id = :id;
        """,
        {
            "id": receipt_id,
            "store_name": values["store_name"],
            "purchase_date": values["purchase_date"],
            "total_amount": values["total_amount"],
            "payment_method": values.get("payment_method"),
            "category": values.get("category"),
            "updated_at": now_iso(),
        },
    )
    conn.commit()
    return result.rowcount > 0


def cancel_receipt(conn: sqlite3.Connection, receipt_id: str) -> bool:
    result = conn.execute(
        """
        UPDATE receipts
        SET status = 'cancelled',
            updated_at = ?
        WHERE id = ?;
        """,
        (now_iso(), receipt_id),
    )
    conn.commit()
    return result.rowcount > 0


def get_stats(
    conn: sqlite3.Connection,
    range_name: str,
    group_by: str | None = None,
    now: date | None = None,
) -> dict[str, Any]:
    start, end = date_range(range_name, now=now)
    params: list[Any] = [start.isoformat(), end.isoformat()]
    total = conn.execute(
        """
        SELECT COALESCE(SUM(total_amount), 0) AS total
        FROM receipts
        WHERE status = 'confirmed'
          AND purchase_date >= ?
          AND purchase_date < ?;
        """,
        params,
    ).fetchone()["total"]

    groups: list[dict[str, Any]] = []
    if group_by in {"category", "store"}:
        column = "category" if group_by == "category" else "store_name"
        rows = conn.execute(
            f"""
            SELECT COALESCE({column}, '未分类') AS name,
                   COALESCE(SUM(total_amount), 0) AS amount
            FROM receipts
            WHERE status = 'confirmed'
              AND purchase_date >= ?
              AND purchase_date < ?
            GROUP BY COALESCE({column}, '未分类')
            ORDER BY amount DESC, name ASC;
            """,
            params,
        ).fetchall()
        groups = [dict(row) for row in rows]

    return {
        "range": range_name,
        "currency": "JPY",
        "start_date": start.isoformat(),
        "end_date": (end - timedelta(days=1)).isoformat(),
        "total": int(total or 0),
        "groups": groups,
    }


def list_receipts_for_export(conn: sqlite3.Connection, range_name: str) -> list[dict[str, Any]]:
    start, end = date_range(range_name)
    rows = conn.execute(
        """
        SELECT purchase_date AS date,
               store_name,
               total_amount,
               payment_method,
               category,
               created_at
        FROM receipts
        WHERE status = 'confirmed'
          AND purchase_date >= ?
          AND purchase_date < ?
        ORDER BY purchase_date ASC, created_at ASC;
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return [dict(row) for row in rows]


def date_range(range_name: str, now: date | None = None) -> tuple[date, date]:
    current = now or datetime.now(tz=JST).date()
    if range_name == "today":
        return current, current + timedelta(days=1)
    if range_name == "month":
        start = current.replace(day=1)
        return start, _add_month(start)
    if range_name == "last_month":
        this_month = current.replace(day=1)
        last_month_start = _add_month(this_month, months=-1)
        return last_month_start, this_month
    raise ValueError("range must be one of: today, month, last_month")


def _add_month(value: date, months: int = 1) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=1)
