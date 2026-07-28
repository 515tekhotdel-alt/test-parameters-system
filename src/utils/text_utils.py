"""
Утилиты для обработки текста
"""

import re
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    Очищает текст от лишних символов

    Args:
        text: Исходный текст

    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""

    # Удаляем множественные пробелы
    text = re.sub(r'\s+', ' ', text)

    # Удаляем пробелы в начале и конце
    text = text.strip()

    return text


def extract_materials(composition_text: str) -> List[dict]:
    """
    Извлекает материалы и их процентное содержание из текста состава

    Args:
        composition_text: Текст состава (например, "65% полиэстер, 35% хлопок")

    Returns:
        List[dict]: Список материалов с процентами
    """
    if not composition_text:
        return []

    materials = []

    # Ищем паттерн: число% материал
    pattern = r'(\d+)[,.]?\s*%\s*([а-яА-ЯёЁa-zA-Z\s\-]+)'
    matches = re.findall(pattern, composition_text)

    for percent, material in matches:
        materials.append({
            "material": clean_text(material),
            "percentage": int(percent)
        })

    return materials


def extract_product_type(product_name: str, keywords: dict) -> Optional[str]:
    """
    Определяет тип изделия по ключевым словам

    Args:
        product_name: Наименование изделия
        keywords: Словарь ключевых слов

    Returns:
        Optional[str]: Тип изделия или None
    """
    if not product_name:
        return None

    product_name_lower = product_name.lower()

    for type_name, type_keywords in keywords.items():
        for keyword in type_keywords:
            if keyword.lower() in product_name_lower:
                return type_name

    return None


def extract_age_group(product_name: str, keywords: dict) -> Optional[str]:
    """
    Определяет возрастную группу по ключевым словам

    Args:
        product_name: Наименование изделия
        keywords: Словарь ключевых слов

    Returns:
        Optional[str]: Возрастная группа или None
    """
    if not product_name:
        return None

    product_name_lower = product_name.lower()

    for age_group, age_keywords in keywords.items():
        for keyword in age_keywords:
            if keyword.lower() in product_name_lower:
                return age_group

    return None


def extract_layer(product_name: str, keywords: dict) -> Optional[str]:
    """
    Определяет слой одежды по ключевым словам

    Args:
        product_name: Наименование изделия
        keywords: Словарь ключевых слов

    Returns:
        Optional[str]: Слой или None
    """
    if not product_name:
        return None

    product_name_lower = product_name.lower()

    for layer, layer_keywords in keywords.items():
        for keyword in layer_keywords:
            if keyword.lower() in product_name_lower:
                return layer

    return None


def extract_construction(product_name: str, keywords: dict) -> Optional[str]:
    """
    Определяет конструкцию изделия по ключевым словам

    Args:
        product_name: Наименование изделия
        keywords: Словарь ключевых слов

    Returns:
        Optional[str]: Конструкция или None
    """
    if not product_name:
        return None

    product_name_lower = product_name.lower()

    for construction, construction_keywords in keywords.items():
        for keyword in construction_keywords:
            if keyword.lower() in product_name_lower:
                return construction

    return None


def has_lining(product_name: str) -> bool:
    """
    Определяет наличие подкладки по ключевым словам

    Args:
        product_name: Наименование изделия

    Returns:
        bool: True если есть подкладка
    """
    if not product_name:
        return False

    lining_keywords = ['подкладк', 'на подкладк', 'подкладочн']
    product_name_lower = product_name.lower()

    for keyword in lining_keywords:
        if keyword.lower() in product_name_lower:
            return True

    return False


def is_fleece(product_name: str) -> bool:
    """
    Определяет наличие ворса/футера по ключевым словам

    Args:
        product_name: Наименование изделия

    Returns:
        bool: True если есть ворс/футер
    """
    if not product_name:
        return False

    fleece_keywords = ['ворсован', 'футерован', 'ворс', 'футер']
    product_name_lower = product_name.lower()

    for keyword in fleece_keywords:
        if keyword.lower() in product_name_lower:
            return True

    return False