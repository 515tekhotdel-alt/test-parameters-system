"""
Обобщение правил: группировка продуктов по категориям
"""

import sys
import json
from pathlib import Path
import pandas as pd
from collections import Counter, defaultdict

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from config.settings import RULES_DIR, PROCESSED_DATA_DIR


def load_data():
    """Загружает данные из Excel"""
    df = pd.read_excel("data/raw/test_data_01.xlsx", dtype=str)
    return df


def extract_category(name: str) -> dict:
    """
    Извлекает обобщенные категории из наименования продукта
    """
    name_lower = name.lower()

    categories = {
        "age": "не_определен",
        "layer": "не_определен",
        "construction": "не_определен",
        "product_type": "не_определен",
        "materials": [],
        "features": []
    }

    # 1. Возраст
    age_keywords = {
        "взрослые": ["взросл", "мужск", "женск"],
        "до_1_года": ["новорожденн", "до 1 года", "до года"],
        "ясельные_1-3": ["ясельн", "1-3"],
        "дошкольные_3-7": ["дошкольн", "3-7"],
        "школьные_7-14": ["школьн", "7-14"],
        "подростки_14-18": ["подростк", "14-18"]
    }
    for age, keywords in age_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["age"] = age
                break
        if categories["age"] != "не_определен":
            break

    # 2. Слой
    layer_keywords = {
        "1_слой": ["первого слоя", "1-го слоя", "бельев"],
        "2_слой": ["второго слоя", "2-го слоя"],
        "3_слой": ["третьего слоя", "3-го слоя"]
    }
    for layer, keywords in layer_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["layer"] = layer
                break
        if categories["layer"] != "не_определен":
            break

    # 3. Конструкция
    constr_keywords = {
        "трикотаж": ["трикотажн"],
        "ткань": ["швейн", "из ткани"],
        "кожа": ["кожан"],
        "мех": ["мехов"],
        "нетканый": ["неткан", "войлок", "фетр"]
    }
    for constr, keywords in constr_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["construction"] = constr
                break
        if categories["construction"] != "не_определен":
            break

    # 4. Тип изделия (обобщенные)
    type_keywords = {
        "белье": ["бель", "трус", "майк", "футболк", "пижам", "полотенц", "простын", "наволочк"],
        "брюки": ["брюк", "штаны"],
        "куртка": ["куртк"],
        "платье": ["плать", "сарафан"],
        "юбка": ["юбк"],
        "рубашка": ["рубашк", "сорочк"],
        "свитер": ["свитер", "джемпер", "пуловер"],
        "пальто": ["пальто"],
        "головной_убор": ["шапк", "кепк", "шляп", "панам", "чепч"],
        "обувь": ["обув", "сапог", "ботинк", "туфл", "кроссовк"],
        "носки": ["носк", "чулк", "гольф", "колготк", "легинс"],
        "перчатки": ["перчатк", "варежк", "рукавиц"],
        "шарф": ["шарф", "платок", "снуд"],
        "костюм": ["костюм", "комплект"],
        "белье_постельное": ["постельн", "пододеяльн"],
        "ткань_материал": ["ткань", "полотно", "материал"]
    }
    for ptype, keywords in type_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                categories["product_type"] = ptype
                break
        if categories["product_type"] != "не_определен":
            break

    # 5. Материалы (извлечение из состава)
    mat_keywords = {
        "хлопок": ["хлопок", "хлопчатобумажн", "хлопков"],
        "лен": ["лен", "льнян"],
        "шерсть": ["шерсть", "шерстян", "овечья", "альпака"],
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
        "кожа": ["кож"],
        "мех": ["мех"],
        "резина": ["резин"],
        "полимерные": ["полимерн"]
    }
    materials = []
    for mat, keywords in mat_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                materials.append(mat)
                break
    categories["materials"] = list(set(materials))

    # 6. Особенности
    features = []
    if "подкладк" in name_lower or "на подкладк" in name_lower:
        features.append("подкладка")
    if "ворсован" in name_lower or "футерован" in name_lower:
        features.append("ворс")
    if "утепл" in name_lower:
        features.append("утеплитель")
    categories["features"] = features

    return categories


def main():
    logger.info("=" * 80)
    logger.info("📊 ОБОБЩЕНИЕ ПРАВИЛ ПО КАТЕГОРИЯМ")
    logger.info("=" * 80)

    # Загружаем данные
    df = load_data()
    products = df["Наименование объекта испытаний"].dropna().unique().tolist()

    logger.info(f"✅ Загружено продуктов: {len(products)}")

    # Извлекаем категории
    product_categories = {}
    for name in products:
        cats = extract_category(name)
        product_categories[name] = cats

    # Группируем по категориям
    groups = defaultdict(list)
    for name, cats in product_categories.items():
        key = f"{cats['age']}|{cats['layer']}|{cats['construction']}|{cats['product_type']}"
        groups[key].append(name)

    logger.info(f"✅ Уникальных групп: {len(groups)}")

    # Статистика по группам
    group_stats = []
    for key, products_list in groups.items():
        age, layer, construction, product_type = key.split("|")

        # Собираем показатели для всех продуктов в группе
        all_params = []
        for name in products_list:
            params = df[df["Наименование объекта испытаний"] == name][
                "Контролируемый показатель"].dropna().unique().tolist()
            all_params.extend(params)

        # Частота показателей
        param_counts = Counter(all_params)
        total_products = len(products_list)

        # Обязательные (> 60% продуктов)
        mandatory = [p for p, c in param_counts.items() if c / total_products >= 0.6]

        # Частые (30-60%)
        frequent = [p for p, c in param_counts.items() if 0.3 <= c / total_products < 0.6]

        group_stats.append({
            "age": age,
            "layer": layer,
            "construction": construction,
            "product_type": product_type,
            "product_count": total_products,
            "mandatory_parameters": sorted(mandatory),
            "frequent_parameters": sorted(frequent)
        })

    # Сохраняем результат
    output_file = RULES_DIR / "generalized_rules.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(group_stats, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Сохранено: {output_file}")

    # Показываем статистику
    print("\n" + "=" * 80)
    print("📊 СТАТИСТИКА ПО ГРУППАМ")
    print("=" * 80)

    for i, g in enumerate(group_stats[:20], 1):
        print(f"\n{i}. {g['product_type']} ({g['age']}, {g['layer']}, {g['construction']})")
        print(f"   Продуктов: {g['product_count']}")
        print(f"   Обязательных показателей: {len(g['mandatory_parameters'])}")
        if g['mandatory_parameters']:
            print(f"   Примеры: {', '.join(g['mandatory_parameters'][:5])}...")


if __name__ == "__main__":
    main()