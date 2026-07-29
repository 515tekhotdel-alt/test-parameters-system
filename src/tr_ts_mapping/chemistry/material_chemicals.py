"""
Загрузчик маппинга: материал → химические вещества
"""

import json
from pathlib import Path


def load_material_chemicals():
    """
    Загружает словарь материал → химические вещества
    """
    filepath = Path(__file__).parent / "material_chemicals.json"

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_chemicals_for_material(material_name: str, tr_ts: str, environment: str):
    """
    Возвращает список химических веществ для материала

    Args:
        material_name: название материала (ключ из словаря)
        tr_ts: "tr_ts_007" или "tr_ts_017"
        environment: "водная_среда" или "воздушная_среда"

    Returns:
        list: список веществ
    """
    mapping = load_material_chemicals()

    if material_name not in mapping:
        return []

    material_data = mapping[material_name]
    chemistry = material_data.get("химия", {})
    tr_ts_data = chemistry.get(tr_ts, {})

    return tr_ts_data.get(environment, [])


def get_all_materials():
    """
    Возвращает список всех материалов с их ключевыми словами
    """
    mapping = load_material_chemicals()

    result = {}
    for material, data in mapping.items():
        result[material] = data.get("ключевые_слова", [])

    return result


def get_material_by_keyword(keyword: str):
    """
    Определяет материал по ключевому слову

    Args:
        keyword: ключевое слово (например, "хлопок")

    Returns:
        str: название материала или None
    """
    mapping = load_material_chemicals()

    keyword_lower = keyword.lower()

    for material, data in mapping.items():
        for kw in data.get("ключевые_слова", []):
            if kw.lower() in keyword_lower:
                return material

    return None


def extract_materials_from_text(text: str):
    """
    Извлекает все материалы из текста

    Args:
        text: текст (наименование продукции)

    Returns:
        list: список найденных материалов
    """
    mapping = load_material_chemicals()
    found_materials = []

    text_lower = text.lower()

    for material, data in mapping.items():
        for kw in data.get("ключевые_слова", []):
            if kw.lower() in text_lower:
                found_materials.append(material)
                break

    return found_materials