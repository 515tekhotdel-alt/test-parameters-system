"""
Создание справочника методов испытаний для показателей
С учетом разделения по ТР ТС 007 и 017
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict


def main():
    # Загружаем данные
    df = pd.read_excel("data/raw/test_data_01.xlsx", dtype=str)

    # Группируем по (показатель, ТР ТС) → метод
    mapping = defaultdict(dict)
    conflicts = []

    for _, row in df.iterrows():
        param = row["Контролируемый показатель"]
        tr_ts = row["ТР ТС"]
        method = row["Методы испытаний"]

        # Пропускаем пустые показатели и заголовки разделов
        if pd.isna(param) or param in ["", "nan"]:
            continue

        # Определяем ключ ТР ТС
        if "007" in str(tr_ts):
            tr_ts_key = "ТР ТС 007/2011"
        elif "017" in str(tr_ts):
            tr_ts_key = "ТР ТС 017/2011"
        else:
            continue

        method_value = method if pd.notna(method) and method != "" else ""

        # Проверяем на конфликты (одинаковый показатель, одинаковый ТР ТС, но разные методы)
        if param in mapping and tr_ts_key in mapping[param]:
            existing = mapping[param][tr_ts_key]
            if existing != method_value and method_value != "" and existing != "":
                conflicts.append({
                    "param": param,
                    "tr_ts": tr_ts_key,
                    "existing": existing,
                    "new": method_value
                })

        mapping[param][tr_ts_key] = method_value

    # Выводим конфликты
    if conflicts:
        print("\n⚠️ НАЙДЕНЫ КОНФЛИКТЫ (одинаковый показатель, но разные методы):")
        for c in conflicts:
            print(f"  {c['param']} ({c['tr_ts']}): {c['existing']} vs {c['new']}")
        print("\n💡 Для конфликтных показателей будет использован первый метод\n")
    else:
        print("\n✅ Конфликтов не найдено\n")

    # Статистика
    total_params = len(mapping)
    params_with_both = sum(1 for p in mapping.values() if len(p) == 2)
    params_with_one = sum(1 for p in mapping.values() if len(p) == 1)

    print("=" * 80)
    print("📊 СТАТИСТИКА")
    print("=" * 80)
    print(f"Всего уникальных показателей: {total_params}")
    print(f"  - с методами для обоих ТР ТС: {params_with_both}")
    print(f"  - только для одного ТР ТС: {params_with_one}")

    # Сохраняем справочник
    output_path = Path("src/classifier/dictionaries/parameter_methods.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dict(mapping), f, ensure_ascii=False, indent=2)

    print(f"\n✅ Справочник сохранен: {output_path}")
    print(f"   Записей: {len(mapping)}")

    # Показываем примеры
    print("\n📋 ПРИМЕРЫ:")
    for i, (param, methods) in enumerate(list(mapping.items())[:10], 1):
        print(f"  {i}. {param}")
        for tr_ts, method in methods.items():
            print(f"     {tr_ts}: {method if method else '(не указан)'}")


if __name__ == "__main__":
    main()