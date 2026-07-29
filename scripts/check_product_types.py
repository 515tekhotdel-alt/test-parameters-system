import json
from pathlib import Path

with open("data/rules/generalized_rules_by_tr_ts.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Собираем все типы из правил
all_types = set()

for tr_ts in ["tr_ts_007", "tr_ts_017"]:
    for rule in data.get(tr_ts, {}).get("rules", []):
        product_type = rule.get("product_type")
        if product_type and product_type != "не_определен":
            all_types.add(product_type)

print("=" * 80)
print("📊 ТИПЫ ИЗДЕЛИЙ В ПРАВИЛАХ")
print("=" * 80)
for t in sorted(all_types):
    print(f"  - {t}")