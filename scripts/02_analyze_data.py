"""
Упрощенный анализ: только показатели
"""

import sys
from pathlib import Path
import pandas as pd
from collections import Counter
import json
import re

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from config.settings import PROCESSED_DATA_DIR


def analyze_parameters_only(filepath: Path):
    """Анализ только показателей (без методов и норм)"""

    logger.info("=" * 80)
    logger.info("📊 АНАЛИЗ ПОКАЗАТЕЛЕЙ (без методов и норм)")
    logger.info("=" * 80)

    df = pd.read_excel(filepath, dtype=str)
    logger.info(f"✅ Загружено: {len(df)} строк")

    # 1. Группировка по продуктам
    grouped = df.groupby("Наименование объекта испытаний")

    product_params = {}
    for name, group in grouped:
        params = group["Контролируемый показатель"].dropna().unique().tolist()
        product_params[name] = params

    logger.info(f"✅ Уникальных продуктов: {len(product_params)}")

    # 2. Все уникальные показатели
    all_params = df["Контролируемый показатель"].dropna().unique().tolist()
    all_params_sorted = sorted(all_params)

    logger.info(f"✅ Уникальных показателей: {len(all_params_sorted)}")

    # 3. Частотность показателей
    param_counts = Counter(df["Контролируемый показатель"].dropna().tolist())

    # 4. Группировка по ТР ТС (детский/взрослый)
    tr_ts_params = {}
    for tr_ts in df["ТР ТС"].unique():
        if pd.notna(tr_ts):
            subset = df[df["ТР ТС"] == tr_ts]
            params = subset["Контролируемый показатель"].dropna().unique().tolist()
            tr_ts_params[tr_ts] = sorted(params)

    # 5. Сохранение
    output = {
        "total_products": len(product_params),
        "total_parameters": len(all_params_sorted),
        "all_parameters": all_params_sorted,
        "parameter_frequency": dict(param_counts.most_common()),
        "by_tr_ts": tr_ts_params,
        "product_parameters": product_params
    }

    # Сохраняем основной JSON
    output_file = PROCESSED_DATA_DIR / "parameters_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Сохранено: {output_file}")

    # 6. Сохраняем список показателей отдельно (для AI)
    params_file = PROCESSED_DATA_DIR / "all_parameters.txt"
    with open(params_file, 'w', encoding='utf-8') as f:
        for p in all_params_sorted:
            f.write(f"{p}\n")
    logger.info(f"✅ Список показателей: {params_file}")

    # 7. Сохраняем матрицу продукт→показатели
    matrix_file = PROCESSED_DATA_DIR / "product_matrix.json"
    with open(matrix_file, 'w', encoding='utf-8') as f:
        json.dump(product_params, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Матрица продуктов: {matrix_file}")

    # 8. Вывод статистики
    logger.info("\n📊 СТАТИСТИКА:")
    logger.info(f"   Продуктов: {len(product_params)}")
    logger.info(f"   Показателей: {len(all_params_sorted)}")

    # Среднее количество показателей на продукт
    avg_params = sum(len(p) for p in product_params.values()) / len(product_params)
    logger.info(f"   Среднее показателей на продукт: {avg_params:.1f}")

    # Топ-10 показателей
    logger.info("\n   ТОП-10 ПОКАЗАТЕЛЕЙ:")
    for i, (param, count) in enumerate(param_counts.most_common(10), 1):
        pct = count / len(df) * 100
        logger.info(f"   {i:2}. {param}: {count} ({pct:.1f}%)")

    # По ТР ТС
    logger.info("\n   ПО ТР ТС:")
    for tr_ts, params in tr_ts_params.items():
        logger.info(f"   {tr_ts}: {len(params)} показателей")

    return output


if __name__ == "__main__":
    EXCEL_FILE = Path("data/raw/test_data_01.xlsx")

    if not EXCEL_FILE.exists():
        logger.error(f"❌ Файл не найден: {EXCEL_FILE}")
        sys.exit(1)

    analyze_parameters_only(EXCEL_FILE)