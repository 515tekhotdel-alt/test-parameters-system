"""
Парсинг правил из текстовых ответов DeepSeek
Извлекает структурированные правила из текста
"""

import sys
import json
import re
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.utils.file_utils import save_json
from config.settings import RULES_DIR


def extract_json_from_text(text: str) -> dict:
    """
    Извлекает JSON из текста, если он там есть
    """
    # Ищем блок с JSON (между ```json и ```)
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass

    # Ищем объект JSON в любом месте текста
    json_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass

    return None


def parse_children_rules(text: str) -> list:
    """
    Извлекает правила для детей из текста
    """
    rules = []

    # Ищем блоки с правилами по ключевым словам
    sections = re.split(
        r'(?=Условия:|Правило|RULE|Для продукции|Для детей|Возрастная группа)',
        text,
        flags=re.IGNORECASE
    )

    for section in sections:
        if len(section.strip()) < 50:
            continue

        rule = {"rule_id": f"CH{len(rules) + 1:03d}"}

        # Ищем возраст
        age_match = re.search(r'(?:возраст|возрастная группа|age)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if age_match:
            rule["age"] = age_match.group(1).strip()

        # Ищем слой
        layer_match = re.search(r'(?:слой|layer)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if layer_match:
            rule["layer"] = layer_match.group(1).strip()

        # Ищем конструкцию
        constr_match = re.search(r'(?:конструкция|тип полотна|вид)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if constr_match:
            rule["construction"] = constr_match.group(1).strip()

        # Ищем тип изделия
        type_match = re.search(r'(?:тип изделия|вид изделия)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if type_match:
            rule["product_type"] = type_match.group(1).strip()

        # Ищем параметры
        params_match = re.search(r'(?:показатели|параметры|parameters)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if params_match:
            params_text = params_match.group(1).strip()
            # Разбиваем на отдельные показатели
            params = re.findall(r'[«"]([^«"»]+)[»"]', params_text)
            if not params:
                params = [p.strip() for p in re.split(r'[,;]\s*', params_text) if p.strip()]
            rule["parameters"] = params[:30]

        if rule and len(rule) > 1:
            rules.append(rule)

    return rules


def parse_adults_rules(text: str) -> list:
    """
    Извлекает правила для взрослых из текста
    """
    rules = []

    sections = re.split(
        r'(?=Условия:|Правило|RULE|Для продукции|Для взрослых|Для одежды|Слой)',
        text,
        flags=re.IGNORECASE
    )

    for section in sections:
        if len(section.strip()) < 50:
            continue

        rule = {"rule_id": f"AD{len(rules) + 1:03d}"}

        # Ищем слой
        layer_match = re.search(r'(?:слой|layer)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if layer_match:
            rule["layer"] = layer_match.group(1).strip()

        # Ищем конструкцию
        constr_match = re.search(r'(?:конструкция|тип полотна|вид)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if constr_match:
            rule["construction"] = constr_match.group(1).strip()

        # Ищем тип изделия
        type_match = re.search(r'(?:тип изделия|вид изделия)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if type_match:
            rule["product_type"] = type_match.group(1).strip()

        # Ищем материалы
        mat_match = re.search(r'(?:материалы|material)[:\s]+([^\n,]+)', section, re.IGNORECASE)
        if mat_match:
            rule["materials"] = mat_match.group(1).strip()

        # Ищем параметры
        params_match = re.search(r'(?:показатели|параметры|parameters)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if params_match:
            params_text = params_match.group(1).strip()
            params = re.findall(r'[«"]([^«"»]+)[»"]', params_text)
            if not params:
                params = [p.strip() for p in re.split(r'[,;]\s*', params_text) if p.strip()]
            rule["parameters"] = params[:30]

        if rule and len(rule) > 1:
            rules.append(rule)

    return rules


def main():
    logger.info("=" * 80)
    logger.info("📊 ИЗВЛЕЧЕНИЕ ПРАВИЛ ИЗ ТЕКСТА")
    logger.info("=" * 80)

    # Загружаем файлы
    children_file = RULES_DIR / "rules_children.json"
    adults_file = RULES_DIR / "rules_adults.json"

    # Проверяем существование файлов
    if not children_file.exists():
        logger.error(f"❌ Файл не найден: {children_file}")
        return

    if not adults_file.exists():
        logger.error(f"❌ Файл не найден: {adults_file}")
        return

    # Загружаем содержимое
    with open(children_file, 'r', encoding='utf-8') as f:
        children_data = json.load(f)

    with open(adults_file, 'r', encoding='utf-8') as f:
        adults_data = json.load(f)

    # Извлекаем текст
    children_text = children_data.get("raw_response", "") if isinstance(children_data, dict) else str(children_data)
    adults_text = adults_data.get("raw_response", "") if isinstance(adults_data, dict) else str(adults_data)

    logger.info(f"👶 Детский текст: {len(children_text)} символов")
    logger.info(f"👨 Взрослый текст: {len(adults_text)} символов")

    # Пробуем извлечь JSON
    children_json = extract_json_from_text(children_text)
    adults_json = extract_json_from_text(adults_text)

    if children_json:
        logger.info("✅ Извлечен JSON для детей")
        save_json(children_json, RULES_DIR / "rules_children_parsed.json")
        children_rules = children_json
    else:
        logger.info("⚠️  JSON не найден, парсим текст для детей")
        children_rules = parse_children_rules(children_text)
        logger.info(f"✅ Извлечено {len(children_rules)} правил для детей")
        save_json(children_rules, RULES_DIR / "rules_children_parsed.json")

    if adults_json:
        logger.info("✅ Извлечен JSON для взрослых")
        save_json(adults_json, RULES_DIR / "rules_adults_parsed.json")
        adults_rules = adults_json
    else:
        logger.info("⚠️  JSON не найден, парсим текст для взрослых")
        adults_rules = parse_adults_rules(adults_text)
        logger.info(f"✅ Извлечено {len(adults_rules)} правил для взрослых")
        save_json(adults_rules, RULES_DIR / "rules_adults_parsed.json")

    # Объединяем
    final_file = RULES_DIR / "final_rules_parsed.json"
    final_data = {
        "version": "2.0",
        "children_rules": children_rules,
        "adults_rules": adults_rules,
        "total_children_rules": len(children_rules) if isinstance(children_rules, list) else 1,
        "total_adults_rules": len(adults_rules) if isinstance(adults_rules, list) else 1
    }
    save_json(final_data, final_file)

    logger.info("\n" + "=" * 80)
    logger.info(f"✅ Финальный файл: {final_file}")
    logger.info(f"   Детских правил: {final_data['total_children_rules']}")
    logger.info(f"   Взрослых правил: {final_data['total_adults_rules']}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()