"""
Загрузчик норм химических веществ
"""

import json
from pathlib import Path


def load_chemistry_norms():
    """
    Загружает словарь норм химических веществ
    """
    filepath = Path(__file__).parent / "chemistry_norms.json"

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_norm_for_substance(substance: str, environment: str = "водная_среда"):
    """
    Возвращает норму для вещества

    Args:
        substance: название вещества
        environment: "водная_среда" или "воздушная_среда"

    Returns:
        str: норма или None
    """
    norms = load_chemistry_norms()

    if substance not in norms:
        return None

    substance_data = norms[substance]
    if isinstance(substance_data, dict):
        return substance_data.get(environment, None)

    return substance_data