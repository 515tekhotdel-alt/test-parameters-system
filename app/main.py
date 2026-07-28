"""
Главный интерфейс приложения
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from app.core import (
    load_rules,
    load_original_order,
    find_matching_rules,
    get_filtered_values,
    sort_parameters_by_order,
    export_to_excel,
    export_to_word
)


def main():
    st.set_page_config(
        page_title="Подбор показателей",
        page_icon="📋",
        layout="wide"
    )

    # Инициализация состояния
    if "tr_ts" not in st.session_state:
        st.session_state.tr_ts = "tr_ts_017"

    if "last_results" not in st.session_state:
        st.session_state.last_results = None
    if "last_params" not in st.session_state:
        st.session_state.last_params = None
    if "last_rule_info" not in st.session_state:
        st.session_state.last_rule_info = None
    if "last_show_age" not in st.session_state:
        st.session_state.last_show_age = False

    if "selected_product_type" not in st.session_state:
        st.session_state.selected_product_type = ""
    if "selected_age" not in st.session_state:
        st.session_state.selected_age = ""
    if "selected_layer" not in st.session_state:
        st.session_state.selected_layer = ""
    if "selected_construction" not in st.session_state:
        st.session_state.selected_construction = ""

    st.title("📋 Подбор контролируемых показателей")
    st.markdown("**Источник:** Протоколы испытаний (520 продуктов, 16 990 записей)")
    st.markdown("---")

    rules_data = load_rules()
    if not rules_data:
        return

    original_order = load_original_order()

    with st.sidebar:
        st.header("🔍 Выберите характеристики")

        st.markdown("### 📌 Выберите регламент")

        col1, col2 = st.columns(2)

        with col1:
            is_children = st.session_state.tr_ts == "tr_ts_007"
            if st.button(
                "👶 Дети",
                use_container_width=True,
                type="primary" if is_children else "secondary"
            ):
                st.session_state.tr_ts = "tr_ts_007"
                st.rerun()

        with col2:
            is_adults = st.session_state.tr_ts == "tr_ts_017"
            if st.button(
                "👨 Взрослые",
                use_container_width=True,
                type="primary" if is_adults else "secondary"
            ):
                st.session_state.tr_ts = "tr_ts_017"
                st.rerun()

        tr_ts_key = st.session_state.tr_ts
        st.markdown("---")

        current_selected = {
            "product_type": st.session_state.selected_product_type,
            "age": st.session_state.selected_age,
            "layer": st.session_state.selected_layer,
            "construction": st.session_state.selected_construction
        }

        filtered_vals = get_filtered_values(rules_data, tr_ts_key, current_selected)

        # ===== ТИП ИЗДЕЛИЯ =====
        # Находим индекс для выбранного значения
        try:
            idx = filtered_vals["product_types"].index(st.session_state.selected_product_type)
        except ValueError:
            idx = 0

        product_type = st.selectbox(
            "📌 Тип изделия",
            filtered_vals["product_types"],
            index=idx
        )
        if product_type != st.session_state.selected_product_type:
            st.session_state.selected_product_type = product_type
            st.rerun()

        # ===== ВОЗРАСТ =====
        age = ""
        if filtered_vals["show_age"]:
            try:
                idx = filtered_vals["ages"].index(st.session_state.selected_age)
            except ValueError:
                idx = 0

            age = st.selectbox(
                "👶 Возрастная группа",
                filtered_vals["ages"],
                index=idx
            )
            if age != st.session_state.selected_age:
                st.session_state.selected_age = age
                st.rerun()

        # ===== СЛОЙ =====
        try:
            idx = filtered_vals["layers"].index(st.session_state.selected_layer)
        except ValueError:
            idx = 0

        layer = st.selectbox(
            "👕 Слой",
            filtered_vals["layers"],
            index=idx
        )
        if layer != st.session_state.selected_layer:
            st.session_state.selected_layer = layer
            st.rerun()

        # ===== КОНСТРУКЦИЯ =====
        try:
            idx = filtered_vals["constructions"].index(st.session_state.selected_construction)
        except ValueError:
            idx = 0

        construction = st.selectbox(
            "🧵 Конструкция",
            filtered_vals["constructions"],
            index=idx
        )
        if construction != st.session_state.selected_construction:
            st.session_state.selected_construction = construction
            st.rerun()

        st.markdown("---")
        st.caption("💡 Поля автоматически фильтруются в зависимости от выбора")

        # ===== КНОПКИ =====
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            search_clicked = st.button(
                "🔍 Найти показатели",
                type="primary",
                use_container_width=True
            )

        with col_btn2:
            reset_clicked = st.button(
                "🔄 Сброс",
                type="secondary",
                use_container_width=True
            )

        if reset_clicked:
            # Сбрасываем все выбранные значения
            st.session_state.selected_product_type = ""
            st.session_state.selected_age = ""
            st.session_state.selected_layer = ""
            st.session_state.selected_construction = ""
            st.session_state.last_results = None
            st.session_state.last_params = None
            st.session_state.last_rule_info = None
            st.session_state.last_show_age = False
            st.rerun()

    # ===== ОБРАБОТКА ПОИСКА =====
    if search_clicked:
        selected = {
            "product_type": st.session_state.selected_product_type,
            "age": st.session_state.selected_age,
            "layer": st.session_state.selected_layer,
            "construction": st.session_state.selected_construction
        }

        if not any(selected.values()):
            st.warning("⚠️ Выберите хотя бы одну характеристику")
            st.session_state.last_results = None
        else:
            matched = find_matching_rules(rules_data, tr_ts_key, selected)

            if matched:
                best = matched[0]
                params = best["rule"].get("mandatory_parameters", [])
                sorted_params = sort_parameters_by_order(params, original_order)

                rule_info = {
                    "product_type": best["rule"].get("product_type", "-"),
                    "age": best["rule"].get("age", "-"),
                    "layer": best["rule"].get("layer", "-"),
                    "construction": best["rule"].get("construction", "-"),
                    "product_count": best["rule"].get("product_count", 0),
                    "score": matched[0]["score"]
                }

                st.session_state.last_results = matched
                st.session_state.last_params = sorted_params
                st.session_state.last_rule_info = rule_info
                st.session_state.last_show_age = filtered_vals["show_age"]
            else:
                st.session_state.last_results = None
                if st.session_state.selected_product_type:
                    st.warning(f"⚠️ Нет правил для типа изделия '{st.session_state.selected_product_type}'")
                elif st.session_state.selected_age:
                    st.warning(f"⚠️ Нет правил для возраста '{st.session_state.selected_age}'")
                else:
                    st.warning("⚠️ Не найдено подходящих правил")
                st.info("💡 Попробуйте выбрать другие значения")

    # ===== ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ =====
    if st.session_state.last_results:
        matched = st.session_state.last_results
        sorted_params = st.session_state.last_params
        rule_info = st.session_state.last_rule_info
        show_age = st.session_state.last_show_age

        st.success(f"✅ Найдено {len(matched)} подходящих правил")

        st.markdown("### 📋 Список показателей")
        df = pd.DataFrame(sorted_params, columns=["Контролируемый показатель"])
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=min(600, len(df) * 35 + 40)
        )

        st.markdown("---")
        st.markdown("### 📤 Экспорт")

        col1, col2 = st.columns(2)

        with col1:
            excel_data = export_to_excel(sorted_params, rule_info)
            st.download_button(
                label="📊 Скачать Excel",
                data=excel_data,
                file_name="показатели.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_excel"
            )

        with col2:
            word_data = export_to_word(sorted_params, rule_info)
            st.download_button(
                label="📄 Скачать Word",
                data=word_data,
                file_name="показатели.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="download_word"
            )

        with st.expander("📖 Информация о правиле", expanded=True):
            rule = matched[0]["rule"]
            st.markdown(f"**Тип изделия:** {rule.get('product_type', '-')}")
            if show_age and rule.get("age"):
                st.markdown(f"**Возраст:** {rule.get('age', '-')}")
            st.markdown(f"**Слой:** {rule.get('layer', '-')}")
            st.markdown(f"**Конструкция:** {rule.get('construction', '-')}")
            st.markdown(f"**Продуктов в группе:** {rule.get('product_count', 0)}")
            st.markdown(f"**Совпадение:** {matched[0]['score']}%")

        if len(matched) > 1:
            st.markdown("---")
            st.markdown(f"### 📚 Другие правила ({len(matched)-1})")

            for item in matched[1:]:
                rule = item["rule"]
                params = rule.get("mandatory_parameters", [])
                sorted_other_params = sort_parameters_by_order(params, original_order)

                with st.expander(
                    f"📋 {rule.get('product_type', '?')} — {item['score']}% "
                    f"({rule.get('product_count', 0)} продуктов)"
                ):
                    st.markdown("**Условия:**")
                    if show_age and rule.get("age"):
                        st.markdown(f"- Возраст: {rule.get('age', '-')}")
                    st.markdown(f"- Слой: {rule.get('layer', '-')}")
                    st.markdown(f"- Конструкция: {rule.get('construction', '-')}")
                    st.markdown(f"- Продуктов в группе: {rule.get('product_count', 0)}")

                    st.markdown(f"**Показатели ({len(sorted_other_params)}):**")
                    if sorted_other_params:
                        df_other = pd.DataFrame(sorted_other_params, columns=["Контролируемый показатель"])
                        st.dataframe(
                            df_other,
                            use_container_width=True,
                            hide_index=True,
                            height=min(300, len(df_other) * 35 + 40)
                        )
                    else:
                        st.caption("Нет обязательных показателей")

    elif not search_clicked:
        st.info("👈 Выберите ТР ТС, характеристики и нажмите 'Найти показатели'")


if __name__ == "__main__":
    main()