"""
Извлечение валидного JSON из ответа DeepSeek
"""

import sys
import json
import re
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.utils.file_utils import save_json
from config.settings import RULES_DIR


def extract_json(text: str) -> dict:
    """
    Извлекает JSON из текста (удаляет markdown и лишние символы)
    """
    # Пробуем найти блок с JSON
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass

    # Пробуем найти любой JSON-объект
    json_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass

    return None


def main():
    logger.info("=" * 80)
    logger.info("📊 ИЗВЛЕЧЕНИЕ JSON ИЗ ОТВЕТОВ DEEPSEEK")
    logger.info("=" * 80)

    files = [
        ("rules_children.json", "rules_children_final.json"),
        ("rules_adults.json", "rules_adults_final.json")
    ]

    extracted = {}

    for input_name, output_name in files:
        input_path = RULES_DIR / input_name
        output_path = RULES_DIR / output_name

        if not input_path.exists():
            logger.error(f"❌ Файл не найден: {input_path}")
            continue

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        text = data.get("raw_response", "") if isinstance(data, dict) else str(data)

        logger.info(f"\n📄 {input_name}: {len(text)} символов")

        # Извлекаем JSON
        json_data = extract_json(text)

        if json_data:
            logger.info(f"✅ JSON извлечен успешно")
            save_json(json_data, output_path)
            extracted[input_name] = json_data

            # Показываем структуру
            if "rules_children" in json_data:
                logger.info(f"   👶 Детских правил: {len(json_data['rules_children'])}")
            if "rules_adults" in json_data:
                logger.info(f"   👨 Взрослых правил: {len(json_data['rules_adults'])}")
        else:
            logger.error(f"❌ Не удалось извлечь JSON из {input_name}")

    # Объединяем
    if extracted:
        final_data = {
            "version": "2.0",
            "source": "DeepSeek API (раздельный анализ)",
            "children": extracted.get("rules_children.json", {}),
            "adults": extracted.get("rules_adults.json", {})
        }

        final_path = RULES_DIR / "final_rules_v2.json"
        save_json(final_data, final_path)

        logger.info("\n" + "=" * 80)
        logger.info(f"✅ Финальный файл: {final_path}")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()