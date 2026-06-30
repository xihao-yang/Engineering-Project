import unittest

from app.parser import parse_receipt_text


class ParserTest(unittest.TestCase):
    def test_parse_basic_japanese_receipt(self) -> None:
        text = """
        セブンイレブン
        2026年6月29日
        合計 842円
        PayPay
        """

        receipt = parse_receipt_text(text)

        self.assertEqual(receipt.store_name, "セブンイレブン")
        self.assertEqual(receipt.purchase_date, "2026-06-29")
        self.assertEqual(receipt.total_amount, 842)
        self.assertEqual(receipt.payment_method, "PayPay")
        self.assertEqual(receipt.category, "便利店")
        self.assertFalse(receipt.needs_review)

    def test_total_ignores_deposit_and_change_lines(self) -> None:
        text = """
        ライフ
        26/06/29
        小計 766円
        合計 842円
        お預り 1,000円
        お釣り 158円
        現金
        """

        receipt = parse_receipt_text(text)

        self.assertEqual(receipt.purchase_date, "2026-06-29")
        self.assertEqual(receipt.total_amount, 842)
        self.assertEqual(receipt.payment_method, "現金")
        self.assertEqual(receipt.category, "超市")

    def test_missing_amount_requires_review(self) -> None:
        receipt = parse_receipt_text("領収書\n2026-06-29\nPayPay")

        self.assertIsNone(receipt.total_amount)
        self.assertTrue(receipt.needs_review)
        self.assertIn("total_amount_not_found", receipt.warnings)


if __name__ == "__main__":
    unittest.main()
