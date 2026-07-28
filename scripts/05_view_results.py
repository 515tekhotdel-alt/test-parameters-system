"""
Просмотр результатов работы DeepSeek
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from config.settings import RULES_DIR


def view_results():
    """Просмотр финальных правил"""

    logger.info("=" * 80)
    logger.info("📊 ПРОСМОТР РЕЗУЛЬТАТОВ")
    logger.info("=" * 80)

    # Проверяем наличие файлов
    files = list(RULES_DIR.glob("*.json"))

    if not files:
        logger.error("❌ Нет JSON-файлов в data/rules/")
        return

    logger.info(f"\n📂 Найдены файлы:")
    for f in files:
        size = f.stat().st_size / 1024
        logger.info(f"   - {f.name} ({size:.1f} KB)")

    # Читаем финальный файл
    final_file = RULES_DIR / "final_rules.json"

    if not final_file.exists():
        logger.error(f"❌ Файл не найден: {final_file}")
        return

    with open(final_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n" + "=" * 80)
    print("📊 ФИНАЛЬНЫЕ ПРАВИЛА (структура)")
    print("=" * 80)

    # Версия
    print(f"\n📌 Версия: {data.get('version', 'не указана')}")

    # Статистика
    if "generated_from" in data:
        gen = data["generated_from"]
        print(f"📌 Сгенерировано из:")
        print(f"   - Продуктов: {gen.get('products', '?')}")
        print(f"   - Показателей: {gen.get('parameters', '?')}")

    # ИТЕРАЦИЯ 1
    if "iteration_1" in data:
        print("\n" + "-" * 80)
        print("🔮 ИТЕРАЦИЯ 1: Анализ ТР ТС → проверка по данным")
        print("-" * 80)

        iter1 = data["iteration_1"]

        # Показываем предложенную структуру
        if "proposed_structure" in iter1:
            structure = iter1["proposed_structure"]
            if "characteristics" in structure:
                print("\n   Предложенные характеристики:")
                for char in structure["characteristics"]:
                    name = char.get("name", "?")
                    values = char.get("values", [])
                    print(f"      - {name}: {', '.join(values[:5])}{'...' if len(values) > 5 else ''}")

        # Показываем анализ
        if "analysis" in iter1:
            analysis = iter1["analysis"]
            print("\n   Анализ расхождений:")
            if "differences" in analysis:
                for diff in analysis["differences"][:5]:
                    print(f"      - {diff}")
            if "recommendations" in analysis:
                print("\n   Рекомендации:")
                for rec in analysis["recommendations"][:5]:
                    print(f"      - {rec}")

    # ИТЕРАЦИЯ 2
    if "iteration_2" in data:
        print("\n" + "-" * 80)
        print("🔮 ИТЕРАЦИЯ 2: Сверка → Финальные правила")
        print("-" * 80)

        iter2 = data["iteration_2"]

        # Финальная структура
        if "final_structure" in iter2:
            structure = iter2["final_structure"]
            if "characteristics" in structure:
                print("\n   ✅ ФИНАЛЬНАЯ СТРУКТУРА ХАРАКТЕРИСТИК:")
                for char in structure["characteristics"]:
                    name = char.get("name", "?")
                    values = char.get("values", [])
                    print(f"      - {name}: {', '.join(values[:5])}{'...' if len(values) > 5 else ''}")

        # Правила
        if "rules" in iter2:
            rules = iter2["rules"]
            print(f"\n   📋 КОЛИЧЕСТВО ПРАВИЛ: {len(rules)}")

            if rules:
                print("\n   📋 ПЕРВЫЕ 5 ПРАВИЛ:")
                for i, rule in enumerate(rules[:5], 1):
                    print(f"\n   {i}. {rule.get('rule_id', f'R{i:03d}')}")
                    print(f"      Условия: {rule.get('conditions', {})}")
                    params = rule.get('parameters', [])
                    print(f"      Показателей: {len(params)}")
                    if params:
                        print(f"      Первые 5: {', '.join(params[:5])}")
                    if 'source' in rule:
                        print(f"      Источник: {rule.get('source', '?')}")
                    if 'confidence' in rule:
                        print(f"      Уверенность: {rule.get('confidence', 1.0)}")

    # Сохраняем краткий отчет
    report_file = RULES_DIR / "rules_summary.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("КРАТКИЙ ОТЧЕТ О ПРАВИЛАХ\n")
        f.write("=" * 80 + "\n\n")

        if "iteration_2" in data and "rules" in data["iteration_2"]:
            rules = data["iteration_2"]["rules"]
            f.write(f"Всего правил: {len(rules)}\n\n")

            for i, rule in enumerate(rules, 1):
                f.write(f"Правило {i}:\n")
                f.write(f"  Условия: {rule.get('conditions', {})}\n")
                params = rule.get('parameters', [])
                f.write(f"  Показателей: {len(params)}\n")
                f.write(f"  Показатели: {', '.join(params[:10])}\n")
                if len(params) > 10:
                    f.write(f"  ... и еще {len(params) - 10}\n")
                f.write("\n")

    logger.info(f"\n✅ Краткий отчет сохранен: {report_file}")


if __name__ == "__main__":
    view_results()