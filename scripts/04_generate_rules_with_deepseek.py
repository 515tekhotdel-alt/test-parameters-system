"""
Двухитерационный анализ с DeepSeek API
Итерация 1: Анализ ТР ТС → предположение структуры → проверка по данным
Итерация 2: Сверка с ТР ТС → сверка с данными → финальный JSON с правилами
"""

import sys
import json
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.utils.file_utils import read_docx, save_json, load_json
from src.ai.deepseek_client import DeepSeekClient
from config.settings import PROCESSED_DATA_DIR, RULES_DIR, DEEPSEEK_API_KEY

# ===== ПРОМПТЫ ДЛЯ ДВУХ ИТЕРАЦИЙ =====

PROMPT_ITERATION_1 = """
Ты — эксперт по техническому регулированию в области легкой промышленности.

ЗАДАНИЕ 1: Проанализируй тексты технических регламентов (ТР ТС 007 и ТР ТС 017) и определи:
- Какие характеристики продукции влияют на набор контролируемых показателей?
- Как ТР ТС классифицирует продукцию?

Текст ТР ТС 007 (дети):
{tr_ts_007}

Текст ТР ТС 017 (взрослые):
{tr_ts_017}

ЗАДАНИЕ 2: Теперь проверь, как эксперты применяют эти требования на практике.
Вот данные из реальных протоколов испытаний (первые 50 продуктов с их показателями):

{products_sample}

Вот полный список всех показателей, которые встречаются в протоколах:
{all_parameters}

Вопросы для анализа:
1. Какие категории продукции выделяются в ТР ТС?
2. Какие категории реально используются экспертами (из данных)?
3. Есть ли расхождения между ТР ТС и практикой?
4. Предложи структуру характеристик для классификации продукции.

Ответ в формате JSON:
{{
  "analysis": {{
    "tr_ts_categories": ["список категорий из ТР ТС"],
    "expert_categories": ["список категорий из данных"],
    "differences": ["расхождения"],
    "recommendations": ["рекомендации"]
  }},
  "proposed_structure": {{
    "characteristics": [
      {{
        "name": "название характеристики",
        "description": "описание",
        "values": ["список значений"],
        "extraction_keywords": {{"значение": ["ключевые слова"]}}
      }}
    ]
  }}
}}
"""

PROMPT_ITERATION_2 = """
Ты — эксперт по техническому регулированию в области легкой промышленности.

В ИТЕРАЦИИ 1 я получил предварительную структуру характеристик:
{structure_from_iteration_1}

ТЕПЕРЬ ЗАДАНИЕ (ИТЕРАЦИЯ 2):
1. СВЕРЬ эту структуру с ТР ТС (еще раз):
   - ТР ТС 007: {tr_ts_007}
   - ТР ТС 017: {tr_ts_017}

2. СВЕРЬ эту структуру с реальными данными из протоколов (еще раз):
   - Все продукты: {all_products_count}
   - Все показатели: {all_parameters_count}
   - Примеры продуктов с показателями: {products_sample}

3. Если есть расхождения — ИСПРАВЬ структуру.

4. На основе ИТОГОВОЙ структуры сформируй ПРАВИЛА подбора показателей.

Правила должны быть в формате:
ЕСЛИ [характеристика1 = значение1] И [характеристика2 = значение2] ...
ТО показатели = [список показателей]

Важно:
- Используй ТОЛЬКО реальные показатели из данных
- Группируй похожие правила
- Укажи для каждого правила, на скольких продуктах оно основано

Ответ в формате JSON:
{{
  "final_structure": {{
    "characteristics": [...]
  }},
  "rules": [
    {{
      "rule_id": "R001",
      "conditions": {{
        "характеристика1": "значение1",
        "характеристика2": "значение2"
      }},
      "parameters": ["показатель1", "показатель2"],
      "source": "основано на N продуктах",
      "confidence": 0.95
    }}
  ]
}}
"""


def run_iteration_1(client, stats, tr_ts_texts, products_sample):
    """Итерация 1: анализ ТР ТС → проверка по данным"""

    logger.info("\n" + "=" * 80)
    logger.info("🔮 ИТЕРАЦИЯ 1: Анализ ТР ТС и проверка по данным")
    logger.info("=" * 80)

    prompt = PROMPT_ITERATION_1.format(
        tr_ts_007=tr_ts_texts.get("TR_TS_007", "")[:20000],
        tr_ts_017=tr_ts_texts.get("TR_TS_017", "")[:20000],
        products_sample=products_sample,
        all_parameters="\n".join([f"- {p}" for p in stats["all_parameters"][:50]])
    )

    logger.info("📤 Отправка запроса в DeepSeek...")
    response = client.chat(prompt, max_tokens=12000)

    # Сохраняем результат
    result_file = RULES_DIR / "iteration_1_result.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(response)
    logger.info(f"✅ Сохранено: {result_file}")

    try:
        result = json.loads(response)
        logger.info("✅ JSON успешно распарсен")
        return result
    except:
        logger.warning("⚠️  Ответ не в формате JSON")
        return {"raw_response": response}


def run_iteration_2(client, structure_from_iteration_1, stats, tr_ts_texts, products_sample):
    """Итерация 2: сверка с ТР ТС → сверка с данными → финальные правила"""

    logger.info("\n" + "=" * 80)
    logger.info("🔮 ИТЕРАЦИЯ 2: Сверка с ТР ТС и данными → Финальные правила")
    logger.info("=" * 80)

    prompt = PROMPT_ITERATION_2.format(
        structure_from_iteration_1=json.dumps(structure_from_iteration_1, ensure_ascii=False, indent=2),
        tr_ts_007=tr_ts_texts.get("TR_TS_007", "")[:20000],
        tr_ts_017=tr_ts_texts.get("TR_TS_017", "")[:20000],
        all_products_count=stats["total_products"],
        all_parameters_count=stats["total_parameters"],
        products_sample=products_sample
    )

    logger.info("📤 Отправка запроса в DeepSeek (это может занять несколько минут)...")
    response = client.chat(prompt, max_tokens=16000)

    # Сохраняем результат
    result_file = RULES_DIR / "iteration_2_result.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(response)
    logger.info(f"✅ Сохранено: {result_file}")

    try:
        result = json.loads(response)
        logger.info("✅ JSON успешно распарсен")
        return result
    except:
        logger.warning("⚠️  Ответ не в формате JSON")
        return {"raw_response": response}


def prepare_products_sample(filepath: Path, sample_size: int = 50):
    """Подготавливает примеры продуктов с показателями"""

    df = pd.read_excel(filepath, dtype=str)

    # Группируем по продуктам
    grouped = df.groupby("Наименование объекта испытаний")

    samples = []
    for i, (name, group) in enumerate(grouped):
        if i >= sample_size:
            break
        params = group["Контролируемый показатель"].dropna().unique().tolist()
        tr_ts = group["ТР ТС"].iloc[0] if len(group) > 0 else ""
        samples.append({
            "product": name[:150] + "..." if len(name) > 150 else name,
            "tr_ts": tr_ts,
            "parameters": params[:20]  # показываем до 20 параметров
        })

    return json.dumps(samples, ensure_ascii=False, indent=2)


def main():
    logger.info("=" * 80)
    logger.info("🚀 ЗАПУСК ДВУХИТЕРАЦИОННОГО АНАЛИЗА С DEEPSEEK")
    logger.info("=" * 80)

    # Проверка ключа
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "ваш_ключ_здесь":
        logger.error("❌ Не задан DEEPSEEK_API_KEY в файле .env")
        return

    client = DeepSeekClient(DEEPSEEK_API_KEY)

    # Загрузка данных
    excel_file = Path("data/raw/test_data_01.xlsx")
    df = pd.read_excel(excel_file, dtype=str)

    stats = {
        "total_products": df["Наименование объекта испытаний"].nunique(),
        "total_parameters": df["Контролируемый показатель"].nunique(),
        "all_parameters": df["Контролируемый показатель"].dropna().unique().tolist()
    }

    logger.info(f"📊 Данные: {stats['total_products']} продуктов, {stats['total_parameters']} показателей")

    # Загрузка ТР ТС
    tr_ts_paths = {
        "TR_TS_007": Path("data/raw/tr_ts_007.docx"),
        "TR_TS_017": Path("data/raw/tr_ts_017.docx")
    }
    tr_ts_texts = {}
    for name, path in tr_ts_paths.items():
        if path.exists():
            tr_ts_texts[name] = read_docx(path)
            logger.info(f"✅ Загружен {name}: {len(tr_ts_texts[name])} символов")

    # Подготовка примера продуктов
    products_sample = prepare_products_sample(excel_file, sample_size=50)

    # ИТЕРАЦИЯ 1
    result_1 = run_iteration_1(client, stats, tr_ts_texts, products_sample)

    # ИТЕРАЦИЯ 2
    result_2 = run_iteration_2(client, result_1, stats, tr_ts_texts, products_sample)

    # Финальный JSON
    final_file = RULES_DIR / "final_rules.json"
    final_data = {
        "version": "1.0",
        "generated_from": {
            "products": stats["total_products"],
            "parameters": stats["total_parameters"]
        },
        "iteration_1": result_1,
        "iteration_2": result_2
    }
    save_json(final_data, final_file)

    logger.info("\n" + "=" * 80)
    logger.info("🎉 ДВУХИТЕРАЦИОННЫЙ АНАЛИЗ ЗАВЕРШЕН")
    logger.info("=" * 80)
    logger.info(f"📄 Финальный файл: {final_file}")


if __name__ == "__main__":
    main()