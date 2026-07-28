"""
Показать все правила
"""

import json
from pathlib import Path

final_file = Path("data/rules/final_rules.json")

with open(final_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

rules = data["iteration_2"]["rules"]

print("=" * 80)
print(f"📋 ВСЕ {len(rules)} ПРАВИЛ")
print("=" * 80)

for i, rule in enumerate(rules, 1):
    print(f"\n{i:2}. {rule.get('rule_id', f'R{i:03d}')}")
    print(f"   Условия:")
    for key, value in rule.get('conditions', {}).items():
        print(f"      {key}: {value}")

    params = rule.get('parameters', [])
    print(f"   Показателей: {len(params)}")
    print(f"   Показатели: {', '.join(params)}")
    print(f"   Источник: {rule.get('source', '?')}")
    print(f"   Уверенность: {rule.get('confidence', 1.0)}")