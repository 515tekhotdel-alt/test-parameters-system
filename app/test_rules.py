"""
Проверка загруженных правил
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config.settings import RULES_DIR

rules_file = RULES_DIR / "final_rules_v3.json"

with open(rules_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("📊 СТРУКТУРА ПРАВИЛ")
print("=" * 80)

children = data.get("children", {}).get("rules_children", [])
adults = data.get("adults", {}).get("rules_adults", [])

print(f"\n👶 Детских правил: {len(children)}")
if children:
    print("\nПервое детское правило:")
    print(json.dumps(children[0], ensure_ascii=False, indent=2))

print(f"\n👨 Взрослых правил: {len(adults)}")
if adults:
    print("\nПервое взрослое правило:")
    print(json.dumps(adults[0], ensure_ascii=False, indent=2))