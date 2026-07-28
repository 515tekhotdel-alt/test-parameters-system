"""
Финальный интерфейс подбора показателей
- Показатели в том же порядке, что и в test_data_01.xlsx
- Таблица с одним столбцом
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from config.settings import RULES_DIR, RAW_DATA_DIR


@st.cache_data
def load_rules():
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
    # Берем уникальные показатели в порядке появления
    params = df["Контролируемый показатель"].dropna().unique().tolist()
    return params


def get_unique_values(rules_data, tr_ts_key):
    rules = rules_data.get(tr_ts_key, {}).get("rules", [])

    product_types = sorted(set(r.get("product_type", "") for r in rules if r.get("product_type") not in ["не_определен", ""]))

    ages = []
    if tr_ts_key == "tr_ts_007":
        ages = sorted(set(r.get("age", "") for r in rules if r.get("age") not in ["не_определен", ""]))

    layers = sorted(set(r.get("layer", "") for r in rules if r.get("layer") not in ["не_определен", ""]))
    constructions = sorted(set(r.get("construction", "") for r in rules if r.get("construction") not in ["не_определен", ""]))

    return {
        "product_types": [""] + product_types,
        "ages": [""] + ages,
        "layers": [""] + layers,
        "constructions": [""] + constructions,
        "show_age": tr_ts_key == "tr_ts_007"
    }


def find_matching_rules(rules_data, tr_ts_key, selected):
    rules = rules_data.get(tr_ts_key, {}).get("rules", [])

    product_type = selected.get("product_type", "")

    if product_type:
        filtered_rules = [r for r in rules if r.get("product_type") == product_type]
    else:
        filtered_rules = rules

    if not filtered_rules:
        return []

    other_conditions = {}
    if selected.get("age"):
        other_conditions["age"] = selected["age"]
    if selected.get("layer"):
        other_conditions["layer"] = selected["layer"]
    if selected.get("construction"):
        other_conditions["construction"] = selected["construction"]

    matched = []
    for rule in filtered_rules:
        if not other_conditions:
            matched.append({"rule": rule, "score": 100})
        else:
            matched_count = sum(1 for field in other_conditions if rule.get(field) == other_conditions[field])
            total = len(other_conditions)
            score = int(matched_count / total * 100)
            matched.append({"rule": rule, "score": score})

    matched.sort(key=lambda x: x["score"], reverse=True)
    return matched


def sort_parameters_by_order(params, original_order):
    """Сортирует показатели в порядке их появления в test_data_01.xlsx"""
    if not original_order:
        return params

    # Создаем словарь для быстрого поиска индекса
    order_map = {p: i for i, p in enumerate(original_order)}

    # Сортируем: сначала те, что есть в original_order (по индексу), затем остальные
    def get_order(param):
        return order_map.get(param, len(original_order))

    return sorted(params, key=get_order)


def main():
    st.set_page_config(page_title="Подбор показателей", page_icon="📋", layout="wide")
    st.title("📋 Подбор контролируемых показателей")
    st.markdown("**Источник:** Протоколы испытаний (520 продуктов, 16 990 записей)")
    st.markdown("---")

    rules_data = load_rules()
    if not rules_data:
        return

    original_order = load_original_order()

    with st.sidebar:
        st.header("🔍 Выберите характеристики")

        tr_ts_options = {
            "tr_ts_007": "👶 ТР ТС 007/2011 (Дети)",
            "tr_ts_017": "👨 ТР ТС 017/2011 (Взрослые)"
        }
        tr_ts_key = st.radio(
            "Выберите регламент",
            options=list(tr_ts_options.keys()),
            format_func=lambda x: tr_ts_options[x],
            index=1
        )
        st.markdown("---")

        unique_vals = get_unique_values(rules_data, tr_ts_key)

        product_type = st.selectbox("📌 Тип изделия", unique_vals["product_types"])

        age = ""
        if unique_vals["show_age"]:
            age = st.selectbox("👶 Возрастная группа", unique_vals["ages"])

        layer = st.selectbox("👕 Слой", unique_vals["layers"])
        construction = st.selectbox("🧵 Конструкция", unique_vals["constructions"])

        st.markdown("---")
        st.caption("💡 Если выберете тип изделия, будут показаны только правила для этого типа")

        search_clicked = st.button("🔍 Найти показатели", type="primary", use_container_width=True)

    if search_clicked:
        selected = {
            "product_type": product_type,
            "age": age,
            "layer": layer,
            "construction": construction
        }

        if not any(selected.values()):
            st.warning("⚠️ Выберите хотя бы одну характеристику")
            return

        matched = find_matching_rules(rules_data, tr_ts_key, selected)

        if matched:
            st.success(f"✅ Найдено {len(matched)} подходящих правил")

            # Показываем лучшее правило
            best = matched[0]

            # Получаем показатели и сортируем по порядку из test_data_01
            params = best["rule"].get("mandatory_parameters", [])
            sorted_params = sort_parameters_by_order(params, original_order)

            # Отображаем как таблицу с одним столбцом
            st.markdown("### 📋 Список показателей")

            # Создаем DataFrame с одним столбцом
            df = pd.DataFrame(sorted_params, columns=["Контролируемый показатель"])

            # Отображаем без индекса
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=min(600, len(df) * 35 + 40)
            )

            # Информация о правиле
            with st.expander("📖 Информация о правиле"):
                rule = best["rule"]
                st.markdown(f"**Тип изделия:** {rule.get('product_type', '-')}")
                if unique_vals["show_age"] and rule.get("age"):
                    st.markdown(f"**Возраст:** {rule.get('age', '-')}")
                st.markdown(f"**Слой:** {rule.get('layer', '-')}")
                st.markdown(f"**Конструкция:** {rule.get('construction', '-')}")
                st.markdown(f"**Продуктов в группе:** {rule.get('product_count', 0)}")
                st.markdown(f"**Совпадение:** {matched[0]['score']}%")

            # Если есть другие правила
            if len(matched) > 1:
                with st.expander(f"📚 Другие правила ({len(matched)-1})"):
                    for item in matched[1:]:
                        rule = item["rule"]
                        st.markdown(f"- **{rule.get('product_type', '?')}** ({item['score']}% совпадение) — {rule.get('product_count', 0)} продуктов")
        else:
            if product_type:
                st.warning(f"⚠️ Нет правил для типа изделия '{product_type}' в выбранном регламенте")
                st.info("💡 Попробуйте выбрать другой тип изделия или оставьте поле пустым")
            else:
                st.warning("⚠️ Не найдено правил, совпадающих с выбранными характеристиками")
                st.info("💡 Попробуйте выбрать другие значения")
    else:
        st.info("👈 Выберите ТР ТС, характеристики и нажмите 'Найти показатели'")

        with st.expander("📖 Статистика по регламентам"):
            for key, label in tr_ts_options.items():
                summary = rules_data.get(key, {}).get("summary", {})
                st.markdown(f"**{label}:**")
                st.markdown(f"- Групп: {summary.get('total_groups', 0)}")
                st.markdown(f"- Продуктов: {summary.get('total_products', 0)}")
                st.markdown(f"- Среднее показателей: {summary.get('avg_mandatory_parameters', 0)}")
                st.markdown("---")


if __name__ == "__main__":
    main()