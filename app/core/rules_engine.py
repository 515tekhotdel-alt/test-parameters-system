"""
Движок поиска правил — с умной фильтрацией
"""

UNDEFINED = "не_определен"


def get_filtered_values(rules_data, tr_ts_key, selected):
    """
    Возвращает доступные значения для каждого поля
    С УЧЕТОМ уже выбранных характеристик (умная фильтрация)
    """
    rules = rules_data.get(tr_ts_key, {}).get("rules", [])

    # Начинаем со всех правил
    filtered = rules

    product_type = selected.get("product_type", "")
    age = selected.get("age", "")
    layer = selected.get("layer", "")
    construction = selected.get("construction", "")

    # Применяем фильтры последовательно (кроме поля, для которого считаем значения)
    # Для каждого поля мы смотрим, какие значения остаются после фильтрации по ДРУГИМ полям

    # --- Значения для product_type ---
    temp = rules
    if age:
        temp = [r for r in temp if r.get("age") == age]
    if layer:
        temp = [r for r in temp if r.get("layer") == layer]
    if construction:
        temp = [r for r in temp if r.get("construction") == construction]
    product_types = sorted(set(r.get("product_type", "") for r in temp if r.get("product_type") not in ["", UNDEFINED]))

    # --- Значения для age ---
    temp = rules
    if product_type:
        temp = [r for r in temp if r.get("product_type") == product_type]
    if layer:
        temp = [r for r in temp if r.get("layer") == layer]
    if construction:
        temp = [r for r in temp if r.get("construction") == construction]
    ages = sorted(set(r.get("age", "") for r in temp if r.get("age") not in ["", UNDEFINED]))

    # --- Значения для layer ---
    temp = rules
    if product_type:
        temp = [r for r in temp if r.get("product_type") == product_type]
    if age:
        temp = [r for r in temp if r.get("age") == age]
    if construction:
        temp = [r for r in temp if r.get("construction") == construction]
    layers = sorted(set(r.get("layer", "") for r in temp if r.get("layer") not in ["", UNDEFINED]))
    has_undefined_layer = any(r.get("layer") == UNDEFINED for r in temp)

    # --- Значения для construction ---
    temp = rules
    if product_type:
        temp = [r for r in temp if r.get("product_type") == product_type]
    if age:
        temp = [r for r in temp if r.get("age") == age]
    if layer:
        temp = [r for r in temp if r.get("layer") == layer]
    constructions = sorted(set(r.get("construction", "") for r in temp if r.get("construction") not in ["", UNDEFINED]))
    has_undefined_construction = any(r.get("construction") == UNDEFINED for r in temp)

    return {
        "product_types": [""] + product_types if product_types else [""],
        "ages": [""] + ages if ages else [""],
        "layers": [""] + layers + ([UNDEFINED] if has_undefined_layer else []),
        "constructions": [""] + constructions + ([UNDEFINED] if has_undefined_construction else []),
        "show_age": tr_ts_key == "tr_ts_007"
    }


def find_matching_rules(rules_data, tr_ts_key, selected):
    """
    Находит правила, соответствующие выбранным характеристикам
    """
    rules = rules_data.get(tr_ts_key, {}).get("rules", [])

    product_type = selected.get("product_type", "")
    age = selected.get("age", "")
    layer = selected.get("layer", "")
    construction = selected.get("construction", "")

    # Последовательная фильтрация
    if product_type:
        rules = [r for r in rules if r.get("product_type") == product_type]

    if age:
        rules = [r for r in rules if r.get("age") == age]

    if layer:
        rules = [r for r in rules if r.get("layer") == layer]

    if construction:
        rules = [r for r in rules if r.get("construction") == construction]

    if not rules:
        return []

    # Считаем процент совпадения
    matched = []
    for rule in rules:
        total = 0
        matched_count = 0

        if product_type:
            total += 1
            if rule.get("product_type") == product_type:
                matched_count += 1
        if age:
            total += 1
            if rule.get("age") == age:
                matched_count += 1
        if layer:
            total += 1
            if rule.get("layer") == layer:
                matched_count += 1
        if construction:
            total += 1
            if rule.get("construction") == construction:
                matched_count += 1

        score = int(matched_count / total * 100) if total > 0 else 100
        matched.append({"rule": rule, "score": score})

    matched.sort(key=lambda x: x["score"], reverse=True)
    return matched


def sort_parameters_by_order(params, original_order):
    """Сортирует показатели в порядке их появления в test_data_01.xlsx"""
    if not original_order:
        return params

    order_map = {p: i for i, p in enumerate(original_order)}

    def get_order(param):
        return order_map.get(param, len(original_order))

    return sorted(params, key=get_order)