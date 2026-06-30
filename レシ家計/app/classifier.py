from __future__ import annotations


CATEGORIES = [
    "便利店",
    "超市",
    "餐饮",
    "咖啡",
    "药妆",
    "日用品",
    "交通",
    "娱乐",
    "医疗",
    "其他",
]


CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "便利店": ["セブン", "7-eleven", "ローソン", "lawson", "ファミマ", "familymart"],
    "超市": ["ライフ", "西友", "イオン", "aeon", "業務スーパー", "まいばすけっと"],
    "药妆": ["マツキヨ", "マツモトキヨシ", "ウエルシア", "welcia", "ココカラ"],
    "咖啡": ["ドトール", "スタバ", "starbucks", "タリーズ", "tully"],
    "交通": ["jr", "東京メトロ", "tokyo metro", "pasmo", "suica"],
    "餐饮": ["マクドナルド", "すき家", "松屋", "吉野家", "サイゼリヤ", "ガスト"],
    "日用品": ["無印", "ニトリ", "ダイソー", "セリア", "cando"],
    "医疗": ["クリニック", "病院", "薬局"],
}


def classify_store(store_name: str | None, ocr_text: str = "") -> str:
    haystack = f"{store_name or ''}\n{ocr_text}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in haystack:
                return category
    return "其他"
