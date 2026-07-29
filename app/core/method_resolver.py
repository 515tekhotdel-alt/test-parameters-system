"""
Разрешение методов для показателей
"""

import json
from pathlib import Path
import streamlit as st


@st.cache_data
def load_methods_mapping():
    """
    Загружает справочник методов из JSON
    """
    filepath = Path("src/classifier/dictionaries/parameter_methods.json")

    if not filepath.exists():
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_method_for_parameter(param_name: str, tr_ts_key: str, methods_mapping: dict) -> str:
    """
    Возвращает метод для показателя с учетом ТР ТС

    Args:
        param_name: название показателя
        tr_ts_key: "ТР ТС 007/2011" или "ТР ТС 017/2011"
        methods_mapping: справочник методов

    Returns:
        str: метод или пустая строка
    """
    if not param_name or param_name not in methods_mapping:
        return ""

    methods = methods_mapping[param_name]

    # Ищем метод для конкретного ТР ТС
    if tr_ts_key in methods and methods[tr_ts_key]:
        return methods[tr_ts_key]

    # Если нет, ищем любой доступный метод
    for tr_ts, method in methods.items():
        if method:
            return method

    return ""


def get_display_name(param_name: str, tr_ts_key: str, methods_mapping: dict) -> str:
    """
    Возвращает отображаемое имя показателя с методом в скобках

    Args:
        param_name: название показателя
        tr_ts_key: "ТР ТС 007/2011" или "ТР ТС 017/2011"
        methods_mapping: справочник методов

    Returns:
        str: "Показатель (метод)" или просто "Показатель"
    """
    method = get_method_for_parameter(param_name, tr_ts_key, methods_mapping)
    if method:
        return f"{param_name} ({method})"
    return param_name


def get_parameters_with_methods(params: list, tr_ts_key: str, methods_mapping: dict) -> list:
    """
    Возвращает список показателей с методами в виде словарей

    Args:
        params: список названий показателей
        tr_ts_key: "ТР ТС 007/2011" или "ТР ТС 017/2011"
        methods_mapping: справочник методов

    Returns:
        list: [{"name": "Показатель", "method": "Метод"}, ...]
    """
    result = []
    for param in params:
        method = get_method_for_parameter(param, tr_ts_key, methods_mapping)
        result.append({
            "name": param,
            "method": method
        })
    return result