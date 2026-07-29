import json
from pathlib import Path

with open("src/classifier/dictionaries/parameter_methods.json", 'r', encoding='utf-8') as f:
    mapping = json.load(f)

print("=" * 80)
print("📊 ПРОВЕРКА СПРАВОЧНИКА МЕТОДОВ")
print("=" * 80)

# Показатели без методов
no_method = []
for param, methods in mapping.items():
    has_method = False
    for tr_ts, method in methods.items():
        if method and method.strip():
            has_method = True
    if not has_method:
        no_method.append(param)

print(f"\nПоказателей без методов: {len(no_method)}")

# Показатели с методом только для одного ТР ТС
one_tr_ts = []
for param, methods in mapping.items():
    if len(methods) == 1:
        one_tr_ts.append(param)

print(f"Показателей только для одного ТР ТС: {len(one_tr_ts)}")

# Показатели с методами для обоих ТР ТС
both = len(mapping) - len(one_tr_ts)
print(f"Показателей для обоих ТР ТС: {both}")

# Примеры
print("\n📋 ПРИМЕРЫ ПОКАЗАТЕЛЕЙ С МЕТОДАМИ:")
for param, methods in list(mapping.items())[:15]:
    method_007 = methods.get("ТР ТС 007/2011", "")
    method_017 = methods.get("ТР ТС 017/2011", "")
    print(f"  {param}")
    print(f"    007: {method_007 if method_007 else '(не указан)'}")
    print(f"    017: {method_017 if method_017 else '(не указан)'}")

# Сохраняем список показателей без методов
if no_method:
    print("\n⚠️ ПОКАЗАТЕЛИ БЕЗ МЕТОДОВ (нужно заполнить вручную):")
    for p in no_method[:20]:
        print(f"  - {p}")
    if len(no_method) > 20:
        print(f"  ... и еще {len(no_method) - 20}")