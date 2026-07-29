# scripts/check_categories.py
import json
from pathlib import Path

with open("data/rules/generalized_rules_by_tr_ts.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("🔍 ПОИСК КУПАЛЬНЫХ И КОРСЕТНЫХ ИЗДЕЛИЙ В ПРАВИЛАХ")
print("=" * 80)

found = []

for tr_ts in ["tr_ts_007", "tr_ts_017"]:
    for rule in data.get(tr_ts, {}).get("rules", []):
        product_type = rule.get("product_type")
        if "купаль" in product_type.lower() or "корсет" in product_type.lower() or "бюст" in product_type.lower():
            found.append({
                "tr_ts": tr_ts,
                "product_type": product_type,
                "count": rule.get("product_count", 0),
                "age": rule.get("age", "?"),
                "layer": rule.get("layer", "?")
            })

if found:
    for f in found:
        print(f"  [{f['tr_ts']}] {f['product_type']} ({f['age']}, {f['layer']}) → {f['count']} продуктов")
else:
    print("  ❌ Не найдено")