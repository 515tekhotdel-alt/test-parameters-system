"""
Финальный интерфейс подбора показателей
С учетом разделения по ТР ТС 007 и 017
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st

from config.settings import RULES_DIR


@st.cache_data
def load_rules():
    """Загружает обобщенные правила с разделением по ТР ТС"""
    filepath = RULES_DIR / "generalized_rules_by_tr_ts.json"
    if not filepath.exists():
        st.error(f"❌ Файл не найден: {filepath}")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_unique_values(rules_data, tr_ts_key):
    """Извлекает уникальные значения для выпадающих списков"""
    rules = rules_data.get(tr_ts_key, {}).get("rules", [])

    product_types = sorted(set(r.get("product_type", "") for r in rules if r.get("product_type") != "не_определен"))
    ages = sorted(set(r.get("age", "") for r in rules if r.get("age") != "не_определен"))
    layers = sorted(set(r.get("layer", "") for r in rules if r.get("layer") != "не_определен"))
    constructions = sorted(set(r.get("construction", "") for r in rules if r.get("construction") != "не_определен"))

    return {
        "product_types": [""] + product_types,
        "ages": [""] + ages,
        "layers": [""] + layers,
        "constructions": [""] + constructions
    }


def find_matching_rules(rules_data, tr_ts_key, selected):
    """Находит правила, соответствующие выбранным характеристикам"""
    rules = rules_data.get(tr_ts_key, {}).get("rules", [])

    matched = []
    for rule in rules:
        score = 0
        total = 0

        if selected.get("product_type") and rule.get("product_type") == selected["product_type"]:
            score += 1
            total += 1
        if selected.get("age") and rule.get("age") == selected["age"]:
            score += 1
            total += 1
        if selected.get("layer") and rule.get("layer") == selected["layer"]:
            score += 1
            total += 1
        if selected.get("construction") and rule.get("construction") == selected["construction"]:
            score += 1
            total += 1

        if total == 0:
            matched.append({"rule": rule, "score": 0, "match_text": "Все правила"})
        elif score > 0:
            pct = int(score / total * 100)
            matched.append({"rule": rule, "score": pct, "match_text": f"{pct}% совпадение"})

    matched.sort(key=lambda x: x["score"], reverse=True)
    return matched


def main():
    st.set_page_config(
        page_title="Подбор показателей",
        page_icon="📋",
        layout="wide"
    )

    st.title("📋 Подбор контролируемых показателей")
    st.markdown("**Источник:** Протоколы испытаний (520 продуктов, 16 990 записей)")
    st.markdown("---")

    # Загружаем правила
    rules_data = load_rules()
    if not rules_data:
        return

    # Боковая панель
    with st.sidebar:
        st.header("🔍 Выберите характеристики")

        # 1. Выбор ТР ТС
        tr_ts_options = {
            "tr_ts_007": "👶 ТР ТС 007/2011 (Дети)",
            "tr_ts_017": "👨 ТР ТС 017/2011 (Взрослые)"
        }
        tr_ts_key = st.radio(
            "Выберите регламент",
            options=list(tr_ts_options.keys()),
            format_func=lambda x: tr_ts_options[x],
            index=1  # по умолчанию взрослые
        )

        st.markdown("---")

        # Получаем уникальные значения для выбранного ТР ТС
        unique_vals = get_unique_values(rules_data, tr_ts_key)

        # 2. Характеристики
        product_type = st.selectbox("Тип изделия", unique_vals["product_types"])
        age = st.selectbox("Возрастная группа", unique_vals["ages"])
        layer = st.selectbox("Слой", unique_vals["layers"])
        construction = st.selectbox("Конструкция", unique_vals["constructions"])

        st.markdown("---")
        st.caption("💡 Чем больше полей заполните, тем точнее будет подбор")

        search_clicked = st.button("🔍 Найти показатели", type="primary", use_container_width=True)

    # Основная область
    if search_clicked:
        selected = {
            "product_type": product_type,
            "age": age,
            "layer": layer,
            "construction": construction
        }

        # Проверяем, что хоть что-то выбрано
        if not any(selected.values()):
            st.warning("⚠️ Выберите хотя бы одну характеристику")
            return

        # Ищем правила
        matched = find_matching_rules(rules_data, tr_ts_key, selected)

        if matched:
            # Считаем количество правил с совпадением > 0
            valid_rules = [m for m in matched if m["score"] > 0]

            if valid_rules:
                st.success(f"✅ Найдено {len(valid_rules)} подходящих правил")

                # Показываем лучшее
                best = valid_rules[0]
                if best["score"] >= 80:
                    st.info(f"🏆 Лучшее совпадение: {best['score']}%")

                # Показываем все правила
                for item in valid_rules[:10]:
                    rule = item["rule"]
                    score = item["score"]

                    with st.expander(f"📋 {rule.get('product_type', '?')} — {score}% совпадение"):
                        st.markdown(f"**Возраст:** {rule.get('age', '-')}")
                        st.markdown(f"**Слой:** {rule.get('layer', '-')}")
                        st.markdown(f"**Конструкция:** {rule.get('construction', '-')}")
                        st.markdown(f"**Продуктов в группе:** {rule.get('product_count', 0)}")

                        st.markdown("**Обязательные показатели:**")
                        params = rule.get("mandatory_parameters", [])
                        if params:
                            cols = st.columns(2)
                            for i, p in enumerate(params):
                                cols[i % 2].markdown(f"- {p}")
                        else:
                            st.caption("Нет обязательных показателей")
            else:
                st.warning("⚠️ Не найдено правил, полностью соответствующих выбранным характеристикам")
                st.info("💡 Попробуйте выбрать менее конкретные характеристики или посмотреть все правила")

                # Показываем топ-5 правил
                st.markdown("**📋 Топ-5 правил в этом регламенте:**")
                for item in matched[:5]:
                    rule = item["rule"]
                    st.markdown(
                        f"- {rule.get('product_type', '?')} ({rule.get('age', '-')}, {rule.get('layer', '-')}) — {rule.get('product_count', 0)} продуктов")
        else:
            st.warning("⚠️ Нет правил для выбранного ТР ТС")

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