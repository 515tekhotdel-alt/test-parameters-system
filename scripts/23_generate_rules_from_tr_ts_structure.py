"""
Генератор правил V2 на основе структуры ТР ТС (без привязки к ПИ).
Создает правила для ВСЕХ типов продукции, описанных в ТР ТС.
"""

import sys
import json
from pathlib import Path
from itertools import product

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.tr_ts_mapping import (
    extract_materials_from_text,
    get_chemicals_for_material,
    get_biology_for_layer,
    get_biology_for_product_type,
)
from config.settings import RULES_DIR


# ===== ЗАГРУЗКА СЛОВАРЕЙ =====

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_tr_ts_products(tr_ts):
    """Загружает словарь продукции для ТР ТС"""
    filepath = Path(f"src/tr_ts_mapping/product_types/tr_ts_{tr_ts}_products.json")
    if not filepath.exists():
        return {}
    return load_json(filepath)


def load_material_chemicals():
    filepath = Path("src/tr_ts_mapping/chemistry/material_chemicals.json")
    return load_json(filepath)


def load_biology_by_layer():
    filepath = Path("src/tr_ts_mapping/biology/biology_by_layer.json")
    return load_json(filepath)


# ===== ОПРЕДЕЛЕНИЕ КАТЕГОРИЙ =====

def get_all_material_categories():
    """Возвращает все возможные категории материалов из словаря"""
    mat_chem = load_material_chemicals()
    return list(mat_chem.keys())


def get_age_groups(tr_ts):
    """Возвращает возрастные группы для ТР ТС"""
    if tr_ts == "tr_ts_007":
        return ["до_1_года", "ясельные_1-3", "дошкольные_3-7", "школьные_7-14", "подростки_14-18"]
    else:  # tr_ts_017
        return ["взрослые"]


def get_layers():
    """Возвращает все слои"""
    return ["1_слой", "2_слой", "3_слой"]


# ===== ГЕНЕРАЦИЯ ПРАВИЛ =====

def generate_rules_for_product_type(product_type, product_data, tr_ts):
    """
    Генерирует правила для одного типа продукции
    """
    rules = []

    age_groups = get_age_groups(tr_ts)
    layers = get_layers()
    materials = get_all_material_categories()

    for age in age_groups:
        for layer in layers:
            for material in materials:
                rule = {
                    "tr_ts": tr_ts,
                    "product_type": product_type,
                    "age": age,
                    "layer": layer,
                    "material": material,
                    "parameters": []
                }

                # 1. Добавляем биологические показатели (из biology_by_layer)
                bio_params = get_biology_for_layer(tr_ts, layer)
                if bio_params:
                    rule["parameters"].extend(list(bio_params.keys()))

                # 2. Добавляем химические показатели (из material_chemicals)
                chem_water = get_chemicals_for_material(material, tr_ts, "водная_среда")
                chem_air = get_chemicals_for_material(material, tr_ts, "воздушная_среда")
                rule["parameters"].extend(chem_water)
                rule["parameters"].extend(chem_air)

                # 3. Убираем дубли
                rule["parameters"] = list(set(rule["parameters"]))

                # 4. Сортируем
                rule["parameters"].sort()

                # 5. Добавляем правило, если есть хоть один параметр
                if rule["parameters"]:
                    rules.append(rule)

    return rules


def generate_all_rules():
    """
    Генерирует правила для всех ТР ТС и типов продукции
    """
    logger.info("=" * 80)
    logger.info("📊 ГЕНЕРАЦИЯ ПРАВИЛ V2 (ПО СТРУКТУРЕ ТР ТС)")
    logger.info("=" * 80)

    all_rules = []

    # Обрабатываем ТР ТС 007
    logger.info("\n🔹 Обработка ТР ТС 007/2011 (Дети)")
    tr_ts = "tr_ts_007"
    products_007 = load_tr_ts_products("007")

    for prod_type, prod_data in products_007.items():
        logger.info(f"  - {prod_type}")
        rules = generate_rules_for_product_type(prod_type, prod_data, tr_ts)
        all_rules.extend(rules)
        logger.info(f"    Сгенерировано {len(rules)} правил")

    # Обрабатываем ТР ТС 017
    logger.info("\n🔹 Обработка ТР ТС 017/2011 (Взрослые)")
    tr_ts = "tr_ts_017"
    products_017 = load_tr_ts_products("017")

    for prod_type, prod_data in products_017.items():
        logger.info(f"  - {prod_type}")
        rules = generate_rules_for_product_type(prod_type, prod_data, tr_ts)
        all_rules.extend(rules)
        logger.info(f"    Сгенерировано {len(rules)} правил")

    # Сохраняем результат
    output_file = RULES_DIR / "rules_from_tr_ts_structure_v2.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_rules, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✅ Сохранено: {output_file}")
    logger.info(f"   Всего правил: {len(all_rules)}")

    # Статистика
    print("\n" + "=" * 80)
    print("📊 СТАТИСТИКА")
    print("=" * 80)
    print(f"Всего правил: {len(all_rules)}")

    # По ТР ТС
    tr_ts_count = {}
    for r in all_rules:
        tr_ts_count[r["tr_ts"]] = tr_ts_count.get(r["tr_ts"], 0) + 1

    for tr_ts, count in tr_ts_count.items():
        label = "ТР ТС 007/2011 (Дети)" if tr_ts == "tr_ts_007" else "ТР ТС 017/2011 (Взрослые)"
        print(f"  {label}: {count} правил")

    return all_rules


if __name__ == "__main__":
    generate_all_rules()