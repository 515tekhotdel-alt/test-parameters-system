# scripts/16_show_raw_response.py
"""
Показывает первые 2000 символов ответа DeepSeek
"""

import json
from pathlib import Path

RULES_DIR = Path("data/rules")

for file_name in ["rules_children.json", "rules_adults.json"]:
    filepath = RULES_DIR / file_name

    if not filepath.exists():
        print(f"❌ {file_name} не найден")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    text = data.get("raw_response", "")

    print("=" * 80)
    print(f"📄 {file_name}")
    print("=" * 80)
    print(f"Длина: {len(text)} символов")
    print("\nПервые 2000 символов:\n")
    print(text[:2000])
    print("\n...\n")