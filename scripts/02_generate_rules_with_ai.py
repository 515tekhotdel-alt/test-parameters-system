"""
Двухитерационный анализ данных с помощью DeepSeek API
Итерация 1: Генерация структуры категорий
Итерация 2: Генерация правил подбора
"""

import sys
import json
from pathlib import Path
import pandas as pd

# Добавляем корень проекта в путь
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.utils.file_utils import read_docx, save_json, load_json
from src.ai.deepseek_client import DeepSeekClient
from src.ai.prompts import ITERATION_1_PROMPT, ITERATION_2_PROMPT
from config.settings import PROCESSED_DATA_DIR, RULES_DIR, DEEPSEEK_API_KEY


class RuleGenerator:
    """Генератор правил с использованием DeepSeek API"""

    def __init__(self, api_key: str):
        self.client = DeepSeekClient(api_key)
        self.data = None
        self.categories = None
        self.rules = None

    def load_data(self, excel_path: Path) -> pd.DataFrame:
        """Загружает данные из Excel"""
        logger.info(f"📂 Загрузка данных из: {excel_path}")
        df = pd.read_excel(excel_path, dtype=str)
        logger.info(f"✅ Загружено {len(df)} строк, {len(df.columns)} колонок")
        self.data = df
        return df

    def prepare_samples(self, df: pd.DataFrame) -> dict:
        """Подготавливает выборку для отправки в AI"""

        # Уникальные наименования
        unique_names = df["Наименование объекта испытаний"].dropna().unique().tolist()

        # Уникальные показатели
        unique_parameters = df["Контролируемый показатель"].dropna().unique().tolist()

        # Уникальные методы
        unique_methods = df["Методы испытаний"].dropna().unique().tolist()

        # Уникальные нормы
        unique_norms = df["Норма по НД"].dropna().unique().tolist()

        stats = {
            "total_rows": len(df),
            "total_products": len(unique_names),
            "total_parameters": len(unique_parameters),
            "total_methods": len(unique_methods),
            "total_norms": len(unique_norms),
            "sample_names": unique_names[:200],
            "sample_parameters": unique_parameters[:200],
            "all_names": unique_names,
            "all_parameters": unique_parameters,
        }

        return stats

    def load_tr_ts(self) -> dict:
        """Загружает тексты ТР ТС из .docx файлов"""
        tr_ts_paths = {
            "TR_TS_007": Path("data/raw/tr_ts_007.docx"),
            "TR_TS_017": Path("data/raw/tr_ts_017.docx")
        }

        texts = {}
        for name, path in tr_ts_paths.items():
            if path.exists():
                texts[name] = read_docx(path)
                logger.info(f"✅ Загружен {name}: {len(texts[name])} символов")
            else:
                logger.warning(f"⚠️  Файл не найден: {path}")
                texts[name] = ""

        return texts

    def iteration_1_generate_categories(self, stats: dict, tr_ts_texts: dict) -> dict:
        """
        ИТЕРАЦИЯ 1: Генерация структуры категорий
        """
        logger.info("\n" + "=" * 80)
        logger.info("🔮 ИТЕРАЦИЯ 1: Генерация структуры категорий")
        logger.info("=" * 80)

        # Формируем промпт
        prompt = ITERATION_1_PROMPT.format(
            total_products=stats["total_products"],
            total_parameters=stats["total_parameters"],
            sample_names="\n".join([f"- {name}" for name in stats["sample_names"][:50]]),
            sample_parameters="\n".join([f"- {param}" for param in stats["sample_parameters"][:50]]),
            all_names="\n".join([f"- {name}" for name in stats["all_names"][:100]]),
            tr_ts_007=tr_ts_texts.get("TR_TS_007", "")[:15000],
            tr_ts_017=tr_ts_texts.get("TR_TS_017", "")[:15000],
        )

        # Сохраняем промпт для отладки
        debug_file = PROCESSED_DATA_DIR / "iteration_1_prompt.txt"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        logger.info(f"📄 Промпт сохранен: {debug_file}")

        # Отправляем запрос
        logger.info("📤 Отправка запроса в DeepSeek...")
        response = self.client.chat(prompt)

        # Сохраняем сырой ответ
        raw_file = PROCESSED_DATA_DIR / "iteration_1_raw_response.txt"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(response)
        logger.info(f"📄 Сырой ответ сохранен: {raw_file}")

        # Парсим JSON
        try:
            categories = json.loads(response)
            logger.info("✅ JSON успешно распарсен")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            categories = {"raw_response": response, "error": str(e)}

        # Сохраняем результат
        categories_file = RULES_DIR / "iteration_1_categories.json"
        save_json(categories, categories_file)

        self.categories = categories
        return categories

    def iteration_2_generate_rules(self, stats: dict, categories: dict, tr_ts_texts: dict) -> dict:
        """
        ИТЕРАЦИЯ 2: Генерация правил подбора
        """
        logger.info("\n" + "=" * 80)
        logger.info("🔮 ИТЕРАЦИЯ 2: Генерация правил подбора")
        logger.info("=" * 80)

        # Подготавливаем примеры данных
        sample_data_lines = []
        sample_data_lines.append(f"Всего продуктов: {stats['total_products']}")
        sample_data_lines.append(f"Всего показателей: {stats['total_parameters']}")
        sample_data_lines.append("")
        sample_data_lines.append("Примеры продуктов и их показателей:")

        # Группируем первые 30 продуктов с их показателями
        if self.data is not None:
            grouped = self.data.groupby("Наименование объекта испытаний")["Контролируемый показатель"].apply(list)
            for i, (name, params) in enumerate(grouped.items()):
                if i >= 30:
                    break
                sample_data_lines.append(f"\n{i + 1}. {name[:100]}...")
                for p in params[:10]:
                    sample_data_lines.append(f"   - {p}")
                if len(params) > 10:
                    sample_data_lines.append(f"   ... и еще {len(params) - 10} показателей")

        sample_data = "\n".join(sample_data_lines)

        # Формируем промпт
        prompt = ITERATION_2_PROMPT.format(
            categories=json.dumps(categories, ensure_ascii=False, indent=2),
            total_rows=stats["total_rows"],
            all_parameters="\n".join([f"- {param}" for param in stats["all_parameters"]]),
            all_names="\n".join([f"- {name}" for name in stats["all_names"]]),
            sample_data=sample_data[:5000],  # Ограничиваем для экономии токенов
            tr_ts_007=tr_ts_texts.get("TR_TS_007", "")[:15000],
            tr_ts_017=tr_ts_texts.get("TR_TS_017", "")[:15000],
        )

        # Сохраняем промпт для отладки
        debug_file = PROCESSED_DATA_DIR / "iteration_2_prompt.txt"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        logger.info(f"📄 Промпт сохранен: {debug_file}")

        # Отправляем запрос
        logger.info("📤 Отправка запроса в DeepSeek (это может занять несколько минут)...")
        response = self.client.chat(prompt, max_tokens=12000)

        # Сохраняем сырой ответ
        raw_file = PROCESSED_DATA_DIR / "iteration_2_raw_response.txt"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(response)
        logger.info(f"📄 Сырой ответ сохранен: {raw_file}")

        # Парсим JSON
        try:
            rules = json.loads(response)
            logger.info("✅ JSON успешно распарсен")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            rules = {"raw_response": response, "error": str(e)}

        # Сохраняем результат
        rules_file = RULES_DIR / "iteration_2_rules.json"
        save_json(rules, rules_file)

        self.rules = rules
        return rules

    def run(self, excel_path: Path):
        """Запуск полного процесса"""

        logger.info("=" * 80)
        logger.info("🚀 ЗАПУСК ГЕНЕРАЦИИ ПРАВИЛ С ИСПОЛЬЗОВАНИЕМ AI")
        logger.info("=" * 80)

        # 1. Загружаем данные
        df = self.load_data(excel_path)

        # 2. Подготавливаем статистику
        stats = self.prepare_samples(df)
        logger.info(f"📊 Статистика:")
        logger.info(f"   - Уникальных продуктов: {stats['total_products']}")
        logger.info(f"   - Уникальных показателей: {stats['total_parameters']}")
        logger.info(f"   - Уникальных методов: {stats['total_methods']}")
        logger.info(f"   - Уникальных норм: {stats['total_norms']}")

        # 3. Загружаем ТР ТС
        tr_ts_texts = self.load_tr_ts()

        # 4. Итерация 1: Генерация категорий
        categories = self.iteration_1_generate_categories(stats, tr_ts_texts)

        # 5. Итерация 2: Генерация правил
        rules = self.iteration_2_generate_rules(stats, categories, tr_ts_texts)

        # 6. Сохраняем финальный результат
        final_file = RULES_DIR / "final_rules.json"
        final_data = {
            "version": "1.0",
            "generated_from": {
                "rows": stats["total_rows"],
                "products": stats["total_products"],
                "parameters": stats["total_parameters"]
            },
            "categories": categories,
            "rules": rules
        }
        save_json(final_data, final_file)

        logger.info("\n" + "=" * 80)
        logger.info("🎉 ГЕНЕРАЦИЯ ПРАВИЛ ЗАВЕРШЕНА")
        logger.info("=" * 80)
        logger.info(f"📄 Финальный файл: {final_file}")

        return categories, rules


if __name__ == "__main__":
    # Путь к вашему Excel-файлу
    EXCEL_FILE = Path("data/raw/test_data_01.xlsx")

    if not EXCEL_FILE.exists():
        logger.error(f"❌ Файл не найден: {EXCEL_FILE}")
        logger.info("Укажите правильный путь к Excel-файлу в переменной EXCEL_FILE")
        sys.exit(1)

    # Проверка ключа API
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "ваш_ключ_здесь":
        logger.error("❌ Не задан DEEPSEEK_API_KEY в файле .env")
        logger.info("Создайте файл .env в корне проекта и добавьте:")
        logger.info("DEEPSEEK_API_KEY=ваш_ключ")
        sys.exit(1)

    # Запуск
    generator = RuleGenerator(DEEPSEEK_API_KEY)
    categories, rules = generator.run(EXCEL_FILE)