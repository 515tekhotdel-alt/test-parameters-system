"""
Экспорт показателей в Excel и Word
"""

import io
import pandas as pd
from docx import Document


def export_to_excel(params, rule_info):
    """
    Экспортирует список показателей в Excel
    ВСЕ НА ОДНОМ ЛИСТЕ
    """
    # Данные для Excel (все на одном листе)
    data = []

    # Информация о правиле
    data.append(["Информация о правиле", ""])
    data.append(["Тип изделия", rule_info.get('product_type', '-')])
    data.append(["Возраст", rule_info.get('age', '-')])
    data.append(["Слой", rule_info.get('layer', '-')])
    data.append(["Конструкция", rule_info.get('construction', '-')])
    data.append(["Продуктов в группе", rule_info.get('product_count', 0)])
    data.append(["Совпадение", f"{rule_info.get('score', 0)}%"])
    data.append([])  # пустая строка
    data.append(["СПИСОК ПОКАЗАТЕЛЕЙ:", ""])

    # Показатели
    for i, param in enumerate(params, 1):
        data.append([f"{i}. {param}", ""])

    # Создаем DataFrame
    df = pd.DataFrame(data, columns=["", ""])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Показатели', index=False, header=False)

    return output.getvalue()


def export_to_word(params, rule_info):
    """
    Экспортирует список показателей в Word
    """
    doc = Document()

    # Заголовок
    title = doc.add_heading('Показатели для испытаний', 0)
    title.alignment = 1

    # Информация о правиле
    doc.add_heading('Информация о продукции', level=1)
    doc.add_paragraph(f'Тип изделия: {rule_info.get("product_type", "-")}')
    doc.add_paragraph(f'Возраст: {rule_info.get("age", "-")}')
    doc.add_paragraph(f'Слой: {rule_info.get("layer", "-")}')
    doc.add_paragraph(f'Конструкция: {rule_info.get("construction", "-")}')
    doc.add_paragraph(f'Продуктов в группе: {rule_info.get("product_count", 0)}')
    doc.add_paragraph(f'Совпадение: {rule_info.get("score", 0)}%')

    doc.add_paragraph()

    # Список показателей
    doc.add_heading('Контролируемые показатели', level=1)

    for i, param in enumerate(params, 1):
        doc.add_paragraph(f'{i}. {param}')

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()