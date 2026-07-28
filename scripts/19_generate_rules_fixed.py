# scripts/19_generate_rules_fixed.py
"""
Раздельный анализ с увеличенным max_tokens и сжатыми промптами
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

PROMPT_CHILDREN = """
Ты — эксперт по техническому регулированию в области детской продукции.

ТР ТС 007 (дети): {tr_ts_007}
Данные: {data_children}

Сформируй JSON с правилами подбора показателей для детской продукции.
Формат: {{"rules_children": [{{"rule_id": "...", "conditions": {{...}}, "parameters": [...], "source": "..."}}]}}
"""

PROMPT_ADULTS = """
Ты — эксперт по техническому регулированию в области взрослой продукции.

ТР ТС 017 (взрослые): {tr_ts_017}
Данные: {data_adults}

Сформируй JSON с правилами подбора показателей для взрослой продукции.
Формат: {{"rules_adults": [{{"rule_id": "...", "conditions": {{...}}, "parameters": [...], "source": "..."}}]}}
"""


def prepare_sample_data(df: pd.DataFrame, max_products: int = 50):
    """Подготавливает примеры продуктов для AI"""
    grouped = df.groupby("Наименование объекта испытаний")
    samples = []
    for i, (name, group) in enumerate(grouped):
        if i >= max_products:
            break
        params = group["Контролируемый показатель"].dropna().unique().tolist()
        samples.append({
            "product": name[:150],
            "parameters": params[:25]
        })
    return json.dumps(samples, ensure_ascii=False, indent=2)


def run():
    logger.info("=" * 80)
    logger.info("🚀 РАЗДЕЛЬНЫЙ АНАЛИЗ (исправленная версия)")
    logger.info("=" * 80)

    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "ваш_ключ_здесь":
        logger.error("❌ Нет DEEPSEEK_API_KEY")
        return

    client = DeepSeekClient(DEEPSEEK_API_KEY)

    # Загрузка данных
    df = pd.read_excel("data/raw/test_data_01.xlsx")
    children_df = df[df["ТР ТС"].str.contains("007", na=False)]
    adults_df = df[df["ТР ТС"].str.contains("017", na=False)]

    logger.info(f"👶 Детских: {len(children_df)} записей")
    logger.info(f"👨 Взрослых: {len(adults_df)} записей")

    # Загрузка ТР ТС
    tr_ts_007 = read_docx(Path("data/raw/tr_ts_007.docx"))[:15000]
    tr_ts_017 = read_docx(Path("data/raw/tr_ts_017.docx"))[:15000]

    # Подготовка данных
    data_children = prepare_sample_data(children_df, max_products=50)
    data_adults = prepare_sample_data(adults_df, max_products=50)

    # Детская продукция
    logger.info("\n👶 Анализ детской продукции...")
    prompt = PROMPT_CHILDREN.format(tr_ts_007=tr_ts_007, data_children=data_children)
    response = client.chat(prompt, max_tokens=32000)
    save_json({"raw_response": response}, RULES_DIR / "rules_children_fixed.json")

    # Взрослая продукция
    logger.info("\n👨 Анализ взрослой продукции...")
    prompt = PROMPT_ADULTS.format(tr_ts_017=tr_ts_017, data_adults=data_adults)
    response = client.chat(prompt, max_tokens=32000)
    save_json({"raw_response": response}, RULES_DIR / "rules_adults_fixed.json")

    logger.info("\n✅ Готово!")


if __name__ == "__main__":
    run()