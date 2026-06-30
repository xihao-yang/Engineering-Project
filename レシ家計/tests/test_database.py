import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.database import create_receipt, get_stats, init_db, open_db


class DatabaseTest(unittest.TestCase):
    def test_stats_sum_and_group_confirmed_receipts_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "receipts.sqlite3"
            with open_db(db_path) as conn:
                init_db(conn)
                create_receipt(
                    conn,
                    {
                        "id": "r1",
                        "image_path": "r1.jpg",
                        "store_name": "セブンイレブン",
                        "purchase_date": "2026-06-03",
                        "total_amount": 842,
                        "payment_method": "PayPay",
                        "category": "便利店",
                        "ocr_text": "",
                        "confidence": 0.9,
                        "status": "confirmed",
                    },
                )
                create_receipt(
                    conn,
                    {
                        "id": "r2",
                        "image_path": "r2.jpg",
                        "store_name": "ライフ",
                        "purchase_date": "2026-06-04",
                        "total_amount": 1200,
                        "payment_method": "現金",
                        "category": "超市",
                        "ocr_text": "",
                        "confidence": 0.9,
                        "status": "confirmed",
                    },
                )
                create_receipt(
                    conn,
                    {
                        "id": "draft",
                        "image_path": "draft.jpg",
                        "store_name": "未確認",
                        "purchase_date": "2026-06-04",
                        "total_amount": 9999,
                        "payment_method": None,
                        "category": "其他",
                        "ocr_text": "",
                        "confidence": 0.2,
                        "status": "draft",
                    },
                )

                stats = get_stats(conn, "month", group_by="category", now=date(2026, 6, 30))

            self.assertEqual(stats["total"], 2042)
            self.assertEqual(
                stats["groups"],
                [
                    {"name": "超市", "amount": 1200},
                    {"name": "便利店", "amount": 842},
                ],
            )


if __name__ == "__main__":
    unittest.main()
