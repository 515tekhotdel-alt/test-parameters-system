"""
Загрузка и кэширование данных
"""

import json
import pandas as pd
import streamlit as st
from pathlib import Path
from config.settings import RULES_DIR, RAW_DATA_DIR


@st.cache_data
def load_rules():
    """Загружает обобщенные правила из JSON"""
    filepath = RULES_DIR / "generalized_rules_by_tr_ts.json"
    if not filepath.exists():
        st.error(f"❌ Файл не найден: {filepath}")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


@st.cache_data
def load_original_order():
    """Загружает порядок показателей из test_data_01.xlsx"""
    excel_path = RAW_DATA_DIR / "test_data_01.xlsx"
    if not excel_path.exists():
        return []

    df = pd.read_excel(excel_path, dtype=str)
    params = df["Контролируемый показатель"].dropna().unique().tolist()
    return params