# app/debug_duplicates.py
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config.settings import RULES_DIR

filepath = RULES_DIR / "generalized_rules_by_tr_ts.json"

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

rules = data.get("tr_ts_017", {}).get("rules", [])

print("=" * 80)
print("ПРАВИЛА ДЛЯ 'брюки' + '2_слой' + 'ткань'")
print("=" * 80)

for r in rules:
    if r.get("product_type") == "брюки" and r.get("layer") == "2_слой" and r.get("construction") == "ткань":
        print(f"\n---")
        print(f"Возраст: {r.get('age')}")
        print(f"Продуктов: {r.get('product_count')}")
        print(f"Показателей: {len(r.get('mandatory_parameters', []))}")
        print(f"Первые 5 показателей: {r.get('mandatory_parameters', [])[:5]}")