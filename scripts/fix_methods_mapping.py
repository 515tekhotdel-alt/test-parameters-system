import json
from pathlib import Path

# Загружаем справочник
filepath = Path("src/classifier/dictionaries/parameter_methods.json")
with open(filepath, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Удаляем заголовок раздела
if "Выделение вредных веществ в воздух" in mapping:
    del mapping["Выделение вредных веществ в воздух"]
    print("✅ Удален 'Выделение вредных веществ в воздух'")
else:
    print("⚠️ 'Выделение вредных веществ в воздух' не найден")

# Сохраняем
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

print(f"✅ Справочник сохранен: {filepath}")
print(f"   Всего показателей: {len(mapping)}")
