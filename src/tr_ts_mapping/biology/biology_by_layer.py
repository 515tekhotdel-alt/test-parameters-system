"""
Загрузчик биологических показателей по слою
"""

import json
from pathlib import Path


def load_biology_by_layer():
    """
    Загружает словарь биологических показателей по слою
    """
    filepath = Path(__file__).parent / "biology_by_layer.json"

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_biology_for_layer(tr_ts: str, layer: str):
    """
    Возвращает биологические показатели для слоя

    Args:
        tr_ts: "tr_ts_007" или "tr_ts_017"
        layer: "1_слой", "2_слой" или "3_слой"

    Returns:
        dict: показатели и их нормы
    """
    mapping = load_biology_by_layer()

    tr_ts_data = mapping.get(tr_ts, {})
    return tr_ts_data.get(layer, {})