import pandas as pd

df = pd.read_excel("data/raw/test_data_01.xlsx", dtype=str)

# Ищем продукты с ключевыми словами
keywords = ["купальн", "плавк", "бюстгальтер", "корсет", "бикини"]
found = []

for kw in keywords:
    mask = df["Наименование объекта испытаний"].str.contains(kw, case=False, na=False)
    products = df[mask]["Наименование объекта испытаний"].unique().tolist()
    if products:
        found.append({"keyword": kw, "count": len(products), "examples": products[:3]})

print("=" * 80)
print("🔍 ПОИСК В ДАННЫХ")
print("=" * 80)

if found:
    for item in found:
        print(f"\n📌 Ключевое слово: '{item['keyword']}'")
        print(f"   Найдено продуктов: {item['count']}")
        print(f"   Примеры:")
        for ex in item['examples']:
            print(f"     - {ex[:100]}...")
else:
    print("❌ Ничего не найдено")