# scripts/11_analyze_materials.py
"""
Анализ материалов из наименований продукции
"""

import re
import json
from pathlib import Path
import pandas as pd
from collections import Counter

# Загружаем данные
df = pd.read_excel("data/raw/test_data_01.xlsx")
products = df["Наименование объекта испытаний"].dropna().unique().tolist()

# Словарь материалов и их ключевых слов
material_keywords = {
    "хлопок": ["хлопок", "хлопчатобумажн", "хлопков"],
    "лен": ["лен", "льнян"],
    "шерсть": ["шерсть", "шерстян", "чистошерст", "полушерст"],
    "шелк": ["шелк", "шёлк"],
    "вискоза": ["вискоз"],
    "лиоцелл": ["лиоцелл"],
    "модал": ["модал"],
    "полиэстер": ["полиэстер", "полиэфир", "пэ", "пэтф"],
    "полиамид": ["полиамид", "нейлон", "капрон"],
    "эластан": ["эластан", "спандекс", "лайкра"],
    "полиуретан": ["полиуретан"],
    "акрил": ["акрил", "полиакрилонитрил"],
    "синтетика": ["синтетич"],
    "искусственные": ["искусственн"],
    "бамбук": ["бамбук"],
    "крапива": ["крапивн"],
    "шерсть_альпака": ["альпака"],
    "овечья_шерсть": ["овечья", "овчина"],
    "металлизированные": ["металлизирован"],
    "резина": ["резин"],
    "полимерные": ["полимерн"],
    "целлюлоза": ["целлюлоз"],
    "силикон": ["силикон"],
    "эва": ["эва"],
    "поролон": ["поролон"],
    "мех": ["мех", "мехов"],
    "кожа": ["кож", "кожан"],
    "ткань": ["ткань", "тканей"],
    "войлок": ["войлок"],
    "нетканый": ["неткан"],
    "фетр": ["фетр"],
}

# Собираем все материалы из наименований
found_materials = Counter()

for product in products:
    product_lower = product.lower()
    for material, keywords in material_keywords.items():
        for keyword in keywords:
            if keyword in product_lower:
                found_materials[material] += 1
                break

# Сортируем по частоте
sorted_materials = sorted(found_materials.items(), key=lambda x: x[1], reverse=True)

print("=" * 80)
print("📊 МАТЕРИАЛЫ В ПРОДУКЦИИ (по частоте)")
print("=" * 80)
print()

for i, (material, count) in enumerate(sorted_materials, 1):
    pct = count / len(products) * 100
    print(f"{i:2}. {material}: {count} продуктов ({pct:.1f}%)")

print()
print("=" * 80)
print(f"Всего уникальных материалов: {len(sorted_materials)}")
print("=" * 80)

# Сохраняем результат
output = {
    "materials": dict(sorted_materials),
    "total_products": len(products),
    "unique_materials": len(sorted_materials)
}

with open("data/processed/materials_analysis.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n✅ Сохранено: data/processed/materials_analysis.json")