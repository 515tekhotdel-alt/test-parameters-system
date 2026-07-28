"""
Раздельный анализ для ТР ТС 007 и ТР ТС 017
"""

import sys
import json
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.utils.file_utils import read_docx, save_json
from src.ai.deepseek_client import DeepSeekClient
from config.settings import RULES_DIR, DEEPSEEK_API_KEY

# ===== ПРОМПТ ДЛЯ ДЕТСКОЙ ПРОДУКЦИИ (ТР ТС 007) =====

PROMPT_CHILDREN = """
Ты — эксперт по техническому регулированию в области детской продукции легкой промышленности.

Текст ТР ТС 007/2011 (дети):
{tr_ts_007}

Данные из реальных протоколов для детской продукции:
{data_children}

ЗАДАНИЕ:
На основе ТР ТС 007 и реальных данных сформируй ПРАВИЛА подбора показателей для детской продукции.

Правила должны быть в формате:
ЕСЛИ [возрастная_группа] И [слой] И [конструкция] И [тип_изделия] И [материалы] ...
ТО показатели = [список показателей]

Для каждого правила укажи:
1. Условия (категории)
2. Список обязательных показателей
3. Источник (на скольких продуктах основано)

Ответ в формате JSON:
{{
  "rules_children": [
    {{
      "rule_id": "CH001",
      "conditions": {{
        "age": "дошкольная",
        "layer": "2_слой",
        "construction": "ткань",
        "product_type": "платье"
      }},
      "parameters": ["Воздухопроницаемость", "Гигроскопичность", ...],
      "source": "основано на 5 продуктах"
    }}
  ]
}}
"""

# ===== ПРОМПТ ДЛЯ ВЗРОСЛОЙ ПРОДУКЦИИ (ТР ТС 017) =====

PROMPT_ADULTS = """
Ты — эксперт по техническому регулированию в области продукции легкой промышленности для взрослых.

Текст ТР ТС 017/2011 (взрослые):
{tr_ts_017}

Данные из реальных протоколов для взрослой продукции:
{data_adults}

ЗАДАНИЕ:
На основе ТР ТС 017 и реальных данных сформируй ПРАВИЛА подбора показателей для взрослой продукции.

Правила должны быть в формате:
ЕСЛИ [слой] И [конструкция] И [тип_изделия] И [материалы] ...
ТО показатели = [список показателей]

Для каждого правила укажи:
1. Условия (категории)
2. Список обязательных показателей
3. Источник (на скольких продуктах основано)

Ответ в формате JSON:
{{
  "rules_adults": [
    {{
      "rule_id": "AD001",
      "conditions": {{
        "layer": "2_слой",
        "construction": "трикотаж",
        "product_type": "свитер"
      }},
      "parameters": ["Воздухопроницаемость", "Индекс токсичности", ...],
      "source": "основано на 12 продуктах"
    }}
  ]
}}
"""


def prepare_data_by_tr_ts(filepath: Path):
    """Разделяет данные на детские и взрослые"""

    df = pd.read_excel(filepath, dtype=str)

    # Детские (ТР ТС 007)
    children_df = df[df["ТР ТС"].str.contains("007", na=False)]

    # Взрослые (ТР ТС 017)
    adults_df = df[df["ТР ТС"].str.contains("017", na=False)]

    logger.info(f"👶 Детских записей: {len(children_df)}")
    logger.info(f"👨 Взрослых записей: {len(adults_df)}")

    return children_df, adults_df


def prepare_sample_data(df: pd.DataFrame, label: str, max_products: int = 50):
    """Подготавливает примеры продуктов для AI"""

    grouped = df.groupby("Наименование объекта испытаний")

    samples = []
    for i, (name, group) in enumerate(grouped):
        if i >= max_products:
            break
        params = group["Контролируемый показатель"].dropna().unique().tolist()
        samples.append({
            "product": name[:200],
            "parameters": params[:30]
        })

    return json.dumps(samples, ensure_ascii=False, indent=2)


def run_separate_analysis():
    """Запуск раздельного анализа"""

    logger.info("=" * 80)
    logger.info("🚀 РАЗДЕЛЬНЫЙ АНАЛИЗ ДЛЯ ДЕТЕЙ И ВЗРОСЛЫХ")
    logger.info("=" * 80)

    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "ваш_ключ_здесь":
        logger.error("❌ Не задан DEEPSEEK_API_KEY")
        return

    client = DeepSeekClient(DEEPSEEK_API_KEY)

    # 1. Загрузка данных
    excel_file = Path("data/raw/test_data_01.xlsx")
    children_df, adults_df = prepare_data_by_tr_ts(excel_file)

    # 2. Загрузка ТР ТС
    tr_ts_007 = read_docx(Path("data/raw/tr_ts_007.docx"))
    tr_ts_017 = read_docx(Path("data/raw/tr_ts_017.docx"))

    # 3. Подготовка данных для AI
    data_children = prepare_sample_data(children_df, "детская", max_products=80)
    data_adults = prepare_sample_data(adults_df, "взрослая", max_products=80)

    results = {}

    # 4. Анализ детской продукции
    logger.info("\n" + "=" * 80)
    logger.info("👶 ЭТАП 1: Анализ детской продукции (ТР ТС 007)")
    logger.info("=" * 80)

    prompt_children = PROMPT_CHILDREN.format(
        tr_ts_007=tr_ts_007[:25000],
        data_children=data_children
    )

    logger.info("📤 Отправка запроса в DeepSeek...")
    response_children = client.chat(prompt_children, max_tokens=32000)

    try:
        results["children"] = json.loads(response_children)
        logger.info("✅ JSON успешно распарсен")
    except:
        logger.warning("⚠️  Ответ не в формате JSON, сохраняем как текст")
        results["children"] = {"raw_response": response_children}

    save_json(results["children"], RULES_DIR / "rules_children.json")

    # 5. Анализ взрослой продукции
    logger.info("\n" + "=" * 80)
    logger.info("👨 ЭТАП 2: Анализ взрослой продукции (ТР ТС 017)")
    logger.info("=" * 80)

    prompt_adults = PROMPT_ADULTS.format(
        tr_ts_017=tr_ts_017[:25000],
        data_adults=data_adults
    )

    logger.info("📤 Отправка запроса в DeepSeek...")
    response_adults = client.chat(prompt_adults, max_tokens=32000)

    try:
        results["adults"] = json.loads(response_adults)
        logger.info("✅ JSON успешно распарсен")
    except:
        logger.warning("⚠️  Ответ не в формате JSON, сохраняем как текст")
        results["adults"] = {"raw_response": response_adults}

    save_json(results["adults"], RULES_DIR / "rules_adults.json")

    # 6. Объединение
    final_rules = {
        "version": "2.0",
        "generated_from": {
            "children_products": children_df["Наименование объекта испытаний"].nunique(),
            "adults_products": adults_df["Наименование объекта испытаний"].nunique()
        },
        "children_rules": results.get("children", {}),
        "adults_rules": results.get("adults", {})
    }

    save_json(final_rules, RULES_DIR / "final_rules_v2.json")

    logger.info("\n" + "=" * 80)
    logger.info("🎉 РАЗДЕЛЬНЫЙ АНАЛИЗ ЗАВЕРШЕН")
    logger.info("=" * 80)
    logger.info(f"📄 Финальный файл: {RULES_DIR / 'final_rules_v2.json'}")


if __name__ == "__main__":
    run_separate_analysis()