# scripts/20_extract_json_v2.py
"""
Извлечение JSON из ответов DeepSeek с несколькими способами
"""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.utils.file_utils import save_json
from config.settings import RULES_DIR


def extract_json_multiple(text: str) -> dict:
    """
    Пытается извлечь JSON разными способами
    """
    # Способ 1: Ищем блок ```json ... ```
    match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass

    # Способ 2: Ищем объект, который начинается с { и заканчивается на }
    # Проверяем баланс скобок
    for i in range(len(text)):
        if text[i] == '{':
            depth = 0
            for j in range(i, len(text)):
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[i:j + 1])
                        except:
                            break

    return None


def main():
    logger.info("=" * 80)
    logger.info("📊 ИЗВЛЕЧЕНИЕ JSON ИЗ ОТВЕТОВ DEEPSEEK")
    logger.info("=" * 80)

    files = [
        ("rules_children_fixed.json", "rules_children_final_v2.json"),
        ("rules_adults_fixed.json", "rules_adults_final_v2.json")
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

        # Показываем начало и конец
        logger.info(f"   Начало: {text[:150]}...")
        logger.info(f"   Конец: ...{text[-150:]}")

        # Извлекаем JSON
        json_data = extract_json_multiple(text)

        if json_data:
            logger.info(f"✅ JSON извлечен успешно")
            save_json(json_data, output_path)
            extracted[input_name] = json_data

            # Показываем структуру
            if "rules_children" in json_data:
                logger.info(f"   👶 Детских правил: {len(json_data['rules_children'])}")
                if json_data["rules_children"]:
                    logger.info(f"   Первое правило: {json_data['rules_children'][0].get('rule_id', '?')}")
            if "rules_adults" in json_data:
                logger.info(f"   👨 Взрослых правил: {len(json_data['rules_adults'])}")
                if json_data["rules_adults"]:
                    logger.info(f"   Первое правило: {json_data['rules_adults'][0].get('rule_id', '?')}")
        else:
            logger.error(f"❌ Не удалось извлечь JSON")

    # Объединяем
    if extracted:
        final_data = {
            "version": "2.0",
            "source": "DeepSeek API (раздельный анализ, исправленный)",
            "children": extracted.get("rules_children_fixed.json", {}),
            "adults": extracted.get("rules_adults_fixed.json", {})
        }

        final_path = RULES_DIR / "final_rules_v3.json"
        save_json(final_data, final_path)

        logger.info("\n" + "=" * 80)
        logger.info(f"✅ Финальный файл: {final_path}")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()