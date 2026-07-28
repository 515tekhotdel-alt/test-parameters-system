# scripts/08_build_dictionaries.py
"""
Построение словарей на основе полного списка продуктов
"""

import json
import re
from pathlib import Path
import pandas as pd

# Загружаем данные
df = pd.read_excel("data/raw/test_data_01.xlsx")
products = df["Наименование объекта испытаний"].dropna().unique().tolist()

# Папка для словарей
DICT_DIR = Path("src/classifier/dictionaries")

# === 1. Строим словари ===

age_dict = {}
layer_dict = {}
construction_dict = {}
product_type_dict = {}
material_dict = {}
feature_dict = {}

for product in products:
    p_lower = product.lower()

    # Возраст
    if "взросл" in p_lower or "мужск" in p_lower or "женск" in p_lower:
        age_dict.setdefault("взрослые", []).extend(["взросл", "мужск", "женск"])
    if "дошкольн" in p_lower:
        age_dict.setdefault("дошкольные_3-7", []).append("дошкольн")
    if "ясельн" in p_lower:
        age_dict.setdefault("ясельные_1-3", []).append("ясельн")
    if "школьн" in p_lower or "школьной" in p_lower or "школьного" in p_lower:
        age_dict.setdefault("школьные_7-14", []).append("школьн")
    if "подростк" in p_lower:
        age_dict.setdefault("подростки_14-18", []).append("подростк")
    if "новорожденн" in p_lower or "до 1 года" in p_lower or "до года" in p_lower:
        age_dict.setdefault("до_1_года", []).extend(["новорожденн", "до 1 года", "до года"])
    if "ясельн" in p_lower:
        age_dict.setdefault("ясельные_1-3", []).append("ясельн")
    if "школьн" in p_lower:
        age_dict.setdefault("школьные_7-14", []).append("школьн")

    # Слой
    if "первого слоя" in p_lower or "1-го слоя" in p_lower:
        layer_dict.setdefault("1_слой", []).extend(["первого слоя", "1-го слоя"])
    if "второго слоя" in p_lower or "2-го слоя" in p_lower:
        layer_dict.setdefault("2_слой", []).extend(["второго слоя", "2-го слоя"])
    if "третьего слоя" in p_lower or "3-го слоя" in p_lower:
        layer_dict.setdefault("3_слой", []).extend(["третьего слоя", "3-го слоя"])

    # Конструкция
    if "трикотажн" in p_lower:
        construction_dict.setdefault("трикотаж", []).append("трикотажн")
    if "швейн" in p_lower or "из ткани" in p_lower:
        construction_dict.setdefault("ткань", []).extend(["швейн", "из ткани"])
    if "кожан" in p_lower:
        construction_dict.setdefault("кожа", []).append("кожан")
    if "мехов" in p_lower:
        construction_dict.setdefault("мех", []).append("мехов")
    if "неткан" in p_lower:
        construction_dict.setdefault("нетканый", []).append("неткан")

    # Тип изделия
    if "белье" in p_lower or "бельев" in p_lower:
        product_type_dict.setdefault("белье", []).extend(["белье", "бельев"])
    if "брюк" in p_lower or "штаны" in p_lower:
        product_type_dict.setdefault("брюки", []).extend(["брюк", "штаны"])
    if "куртк" in p_lower:
        product_type_dict.setdefault("куртка", []).append("куртк")
    if "свитер" in p_lower:
        product_type_dict.setdefault("свитер", []).append("свитер")
    if "плать" in p_lower:
        product_type_dict.setdefault("платье", []).append("плать")
    if "рубашк" in p_lower or "сорочк" in p_lower:
        product_type_dict.setdefault("рубашка", []).extend(["рубашк", "сорочк"])
    if "пальто" in p_lower:
        product_type_dict.setdefault("пальто", []).append("пальто")
    if "носк" in p_lower or "чулк" in p_lower:
        product_type_dict.setdefault("носки", []).extend(["носк", "чулк"])
    if "трус" in p_lower:
        product_type_dict.setdefault("трусы", []).append("трус")
    if "футболк" in p_lower or "майк" in p_lower:
        product_type_dict.setdefault("футболка", []).extend(["футболк", "майк"])
    if "обув" in p_lower or "сапог" in p_lower or "ботинк" in p_lower:
        product_type_dict.setdefault("обувь", []).extend(["обув", "сапог", "ботинк"])
    if "шапк" in p_lower or "кепк" in p_lower or "шляп" in p_lower:
        product_type_dict.setdefault("головной_убор", []).extend(["шапк", "кепк", "шляп"])

    # Особенности
    if "подкладк" in p_lower or "на подкладк" in p_lower:
        feature_dict.setdefault("подкладка", []).extend(["подкладк", "на подкладк"])
    if "ворсован" in p_lower or "футерован" in p_lower:
        feature_dict.setdefault("ворс", []).extend(["ворсован", "футерован"])
    if "полиуретан" in p_lower:
        feature_dict.setdefault("полиуретановые_нити", []).append("полиуретан")
    if "джинсов" in p_lower or "вельвет" in p_lower:
        feature_dict.setdefault("джинса_вельвет", []).extend(["джинсов", "вельвет"])

# Убираем дубликаты
for d in [age_dict, layer_dict, construction_dict, product_type_dict, feature_dict]:
    for k in d:
        d[k] = list(set(d[k]))

# === 2. Сохраняем словари ===

DICT_DIR.mkdir(parents=True, exist_ok=True)

dicts = {
    "age_keywords.json": age_dict,
    "layer_keywords.json": layer_dict,
    "construction_keywords.json": construction_dict,
    "product_types.json": product_type_dict,
    "features_keywords.json": feature_dict
}

for name, data in dicts.items():
    path = DICT_DIR / name
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ {name}: {len(data)} категорий")

print("\n🎉 Словари сохранены в src/classifier/dictionaries/")