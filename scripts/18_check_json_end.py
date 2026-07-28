"""
Проверка окончания JSON в ответе DeepSeek
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

    # Проверяем начало и конец
    print("\n🔍 НАЧАЛО (первые 200 символов):")
    print(text[:200])

    print("\n🔍 КОНЕЦ (последние 300 символов):")
    print(text[-300:])

    # Проверяем баланс скобок
    open_braces = text.count('{')
    close_braces = text.count('}')
    print(f"\n📊 Баланс скобок: {{ = {open_braces}, }} = {close_braces}")

    if open_braces == close_braces:
        print("✅ Скобки сбалансированы — JSON должен быть валидным")
    else:
        print(f"⚠️  Скобки НЕ сбалансированы (разница: {open_braces - close_braces})")

    print("\n" + "-" * 80)