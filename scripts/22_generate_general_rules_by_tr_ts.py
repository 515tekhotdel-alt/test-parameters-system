"""
Обобщение правил с разделением по ТР ТС 007 и 017
Словари загружаются из JSON-файлов (единый источник правды)
"""

import sys
import json
from pathlib import Path
import pandas as pd
from collections import Counter, defaultdict

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from config.settings import RULES_DIR


# ===== ЗАГОЛОВКИ РАЗДЕЛОВ (НЕ ПОКАЗАТЕЛИ) =====
EXCLUDED_PARAMETERS = [
    "Выделение вредных веществ в воду",
    "Выделение вредных веществ в воздух",
    "Миграция вредных веществ",
    "Биологические показатели безопасности",
    "Экстрагируемые вещества",
]


def load_data():
    """Загружает данные из Excel"""
    df = pd.read_excel("data/raw/test_data_01.xlsx", dtype=str)
    return df


def load_dictionaries():
    """
    Загружает все словари из JSON-файлов
    """
    dict_dir = Path(__file__).parent.parent / "src" / "classifier" / "dictionaries"

    with open(dict_dir / "age_keywords.json", 'r', encoding='utf-8') as f:
        age_keywords = json.load(f)

    with open(dict_dir / "layer_keywords.json", 'r', encoding='utf-8') as f:
        layer_keywords = json.load(f)

    with open(dict_dir / "construction_keywords.json", 'r', encoding='utf-8') as f:
        construction_keywords = json.load(f)

    with open(dict_dir / "product_types.json", 'r', encoding='utf-8') as f:
        product_types = json.load(f)

    with open(dict_dir / "features_keywords.json", 'r', encoding='utf-8') as f:
        features_keywords = json.load(f)

    with open(dict_dir / "material_keywords.json", 'r', encoding='utf-8') as f:
        material_keywords = json.load(f)

    with open(dict_dir / "purpose_keywords.json", 'r', encoding='utf-8') as f:
        purpose_keywords = json.load(f)

    return age_keywords, layer_keywords, construction_keywords, product_types, features_keywords, material_keywords, purpose_keywords


def get_threshold(total_products):
    """
    Динамический порог обязательности в зависимости от размера группы

    Args:
        total_products: количество продуктов в группе

    Returns:
        float: порог (0.3-0.6)
    """
    if total_products >= 20:
        return 0.6
    elif total_products >= 10:
        return 0.5
    elif total_products >= 5:
        return 0.4
    else:
        return 0.3


def extract_category(name, age_keywords, layer_keywords, construction_keywords, product_types, features_keywords, material_keywords, purpose_keywords) -> dict:
    """
    Извлекает обобщенные категории из наименования продукта
    Использует загруженные словари
    """
    name_lower = name.lower()

    categories = {
        "age": "не_определен",
        "layer": "не_определен",
        "construction": "не_определен",
        "product_type": "не_определен",
        "purpose": "не_определен",
        "materials": [],
        "features": []
    }

    # 1. Возраст
    for age, keywords in age_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["age"] = age
                break
        if categories["age"] != "не_определен":
            break

    # 2. Слой
    for layer, keywords in layer_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["layer"] = layer
                break
        if categories["layer"] != "не_определен":
            break

    # 3. Конструкция
    for constr, keywords in construction_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["construction"] = constr
                break
        if categories["construction"] != "не_определен":
            break

    # 4. Тип изделия
    for ptype, keywords in product_types.items():
        for kw in keywords:
            if kw in name_lower:
                categories["product_type"] = ptype
                break
        if categories["product_type"] != "не_определен":
            break

    # 5. Назначение (purpose)
    for purpose, keywords in purpose_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["purpose"] = purpose
                break
        if categories["purpose"] != "не_определен":
            break

    # 6. Материалы
    materials = []
    for mat, keywords in material_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                materials.append(mat)
                break
    categories["materials"] = list(set(materials))

    # 7. Особенности
    features = []
    for feature, keywords in features_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                features.append(feature)
                break
    categories["features"] = features

    return categories


def main():
    logger.info("=" * 80)
    logger.info("📊 ОБОБЩЕНИЕ ПРАВИЛ С РАЗДЕЛЕНИЕМ ПО ТР ТС")
    logger.info("=" * 80)

    # Загружаем словари
    age_keywords, layer_keywords, construction_keywords, product_types, features_keywords, material_keywords, purpose_keywords = load_dictionaries()
    logger.info("✅ Словари загружены из JSON")

    # Загружаем данные
    df = load_data()

    # Разделяем по ТР ТС
    children_df = df[df["ТР ТС"].str.contains("007", na=False)]
    adults_df = df[df["ТР ТС"].str.contains("017", na=False)]

    logger.info(f"👶 Детских (ТР ТС 007): {len(children_df)} записей, {children_df['Наименование объекта испытаний'].nunique()} продуктов")
    logger.info(f"👨 Взрослых (ТР ТС 017): {len(adults_df)} записей, {adults_df['Наименование объекта испытаний'].nunique()} продуктов")

    results = {
        "tr_ts_007": {"rules": [], "summary": {}},
        "tr_ts_017": {"rules": [], "summary": {}}
    }

    for tr_ts_name, df_group in [("tr_ts_007", children_df), ("tr_ts_017", adults_df)]:
        logger.info(f"\n{'='*80}")
        logger.info(f"📋 ОБРАБОТКА: {tr_ts_name}")
        logger.info(f"{'='*80}")

        products = df_group["Наименование объекта испытаний"].dropna().unique().tolist()

        # Извлекаем категории
        product_categories = {}
        for name in products:
            cats = extract_category(
                name,
                age_keywords,
                layer_keywords,
                construction_keywords,
                product_types,
                features_keywords,
                material_keywords,
                purpose_keywords
            )
            product_categories[name] = cats

        # Группируем
        if tr_ts_name == "tr_ts_007":
            groups = defaultdict(list)
            for name, cats in product_categories.items():
                key = f"{cats['age']}|{cats['layer']}|{cats['construction']}|{cats['product_type']}"
                groups[key].append(name)
        else:
            groups = defaultdict(list)
            for name, cats in product_categories.items():
                age = "взрослые" if cats['age'] in ["взрослые", "не_определен"] else cats['age']
                key = f"{age}|{cats['layer']}|{cats['construction']}|{cats['product_type']}"
                groups[key].append(name)

        logger.info(f"✅ Уникальных групп: {len(groups)}")

        # Статистика по группам
        group_stats = []
        for key, products_list in groups.items():
            age, layer, construction, product_type = key.split("|")

            all_params = []
            for name in products_list:
                params = df_group[df_group["Наименование объекта испытаний"] == name]["Контролируемый показатель"].dropna().unique().tolist()
                params = [p for p in params if p not in EXCLUDED_PARAMETERS]
                all_params.extend(params)

            param_counts = Counter(all_params)
            total_products = len(products_list)

            threshold = get_threshold(total_products)
            mandatory = [p for p, c in param_counts.items() if c / total_products >= threshold]
            frequent = [p for p, c in param_counts.items() if threshold * 0.5 <= c / total_products < threshold]

            group_stats.append({
                "tr_ts": tr_ts_name,
                "age": age,
                "layer": layer,
                "construction": construction,
                "product_type": product_type,
                "product_count": total_products,
                "mandatory_parameters": sorted(mandatory),
                "frequent_parameters": sorted(frequent)
            })

        group_stats.sort(key=lambda x: x["product_count"], reverse=True)

        results[tr_ts_name]["rules"] = group_stats

        total_groups = len(group_stats)
        total_products = sum(g["product_count"] for g in group_stats)
        avg_params = sum(len(g["mandatory_parameters"]) for g in group_stats) / total_groups if total_groups > 0 else 0

        results[tr_ts_name]["summary"] = {
            "total_groups": total_groups,
            "total_products": total_products,
            "avg_mandatory_parameters": round(avg_params, 1)
        }

        logger.info(f"   Групп: {total_groups}")
        logger.info(f"   Продуктов: {total_products}")
        logger.info(f"   Среднее количество обязательных показателей: {avg_params:.1f}")
        logger.info(f"   Порог обязательности: динамический (0.3-0.6)")

    # Сохраняем результат
    output_file = RULES_DIR / "generalized_rules_by_tr_ts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✅ Сохранено: {output_file}")

    # Сводка
    print("\n" + "=" * 80)
    print("📊 СВОДКА ПО ТР ТС")
    print("=" * 80)

    for tr_ts_name in ["tr_ts_007", "tr_ts_017"]:
        summary = results[tr_ts_name]["summary"]
        print(f"\n{tr_ts_name.upper()}:")
        print(f"   Групп: {summary['total_groups']}")
        print(f"   Продуктов: {summary['total_products']}")
        print(f"   Среднее показателей: {summary['avg_mandatory_parameters']}")

    print("\n" + "=" * 80)
    print("📊 ТОП-10 ГРУПП ПО КОЛИЧЕСТВУ ПРОДУКТОВ")
    print("=" * 80)

    all_rules = results["tr_ts_007"]["rules"] + results["tr_ts_017"]["rules"]
    all_rules.sort(key=lambda x: x["product_count"], reverse=True)

    for i, g in enumerate(all_rules[:10], 1):
        tr_ts_label = "007" if g["tr_ts"] == "tr_ts_007" else "017"
        print(f"\n{i}. [{tr_ts_label}] {g['product_type']} ({g['age']}, {g['layer']}, {g['construction']})")
        print(f"   Продуктов: {g['product_count']}")
        print(f"   Обязательных показателей: {len(g['mandatory_parameters'])}")
        if g['mandatory_parameters']:
            print(f"   Примеры: {', '.join(g['mandatory_parameters'][:5])}...")


if __name__ == "__main__":
    main()