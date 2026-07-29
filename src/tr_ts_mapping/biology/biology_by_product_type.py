"""
Загрузчик биологических показателей по типу продукции
"""

import json
from pathlib import Path


def load_biology_by_product_type():
    """
    Загружает словарь биологических показателей по типу продукции
    """
    filepath = Path(__file__).parent / "biology_by_product_type.json"

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_biology_for_product_type(product_type: str):
    """
    Возвращает биологические показатели для типа продукции

    Args:
        product_type: тип продукции (например, "полотенца", "обувь")

    Returns:
        dict: показатели и их нормы
    """
    mapping = load_biology_by_product_type()
    return mapping.get(product_type, {})