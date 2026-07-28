# scripts/09_check_dictionaries.py
"""
Проверка словарей
"""

import json
from pathlib import Path

DICT_DIR = Path("src/classifier/dictionaries")

print("=" * 80)
print("📂 ПРОВЕРКА СЛОВАРЕЙ")
print("=" * 80)

for filepath in DICT_DIR.glob("*.json"):
    print(f"\n📄 {filepath.name}")
    print("-" * 40)

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("   ⚠️  ПУСТО! Словарь не заполнен.")
        continue

    print(f"   Категорий: {len(data)}")

    for category, keywords in list(data.items())[:5]:
        print(f"      • {category}: {keywords[:5]}{'...' if len(keywords) > 5 else ''}")

    if len(data) > 5:
        print(f"      ... и еще {len(data) - 5} категорий")