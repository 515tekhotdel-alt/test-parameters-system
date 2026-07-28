"""
Проверка загруженных данных
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
from src.utils.file_utils import read_docx, get_files_by_extension
from config.settings import RAW_DATA_DIR, RULES_DIR, PROCESSED_DATA_DIR


def check_excel_data(filepath: Path):
    """Проверяет Excel-файл с протоколами"""

    logger.info("=" * 80)
    logger.info("📂 ПРОВЕРКА EXCEL-ФАЙЛА")
    logger.info("=" * 80)

    if not filepath.exists():
        logger.error(f"❌ Файл не найден: {filepath}")
        return None

    logger.info(f"✅ Файл найден: {filepath}")
    logger.info(f"   Размер: {filepath.stat().st_size / 1024 / 1024:.2f} MB")

    # Загружаем Excel
    df = pd.read_excel(filepath, dtype=str)

    logger.info(f"\n📊 СТРУКТУРА ДАННЫХ:")
    logger.info(f"   - Строк: {len(df)}")
    logger.info(f"   - Колонок: {len(df.columns)}")
    logger.info(f"   - Колонки: {list(df.columns)}")

    # Проверяем наличие обязательных колонок
    expected_cols = ["Наименование объекта испытаний", "Контролируемый показатель", "Методы испытаний", "Норма по НД"]
    missing_cols = [col for col in expected_cols if col not in df.columns]

    if missing_cols:
        logger.warning(f"⚠️  Отсутствуют колонки: {missing_cols}")
        logger.info("   Доступные колонки:")
        for col in df.columns:
            logger.info(f"   - {col}")
    else:
        logger.info("✅ Все обязательные колонки присутствуют")

    # Статистика по колонкам
    logger.info(f"\n📊 СТАТИСТИКА ПО КОЛОНКАМ:")
    for col in df.columns:
        unique_count = df[col].nunique()
        null_count = df[col].isna().sum()
        sample = df[col].dropna().head(3).tolist()
        logger.info(f"   {col}:")
        logger.info(f"      Уникальных: {unique_count}")
        logger.info(f"      Пустых: {null_count} ({null_count / len(df) * 100:.1f}%)")
        logger.info(f"      Примеры: {sample}")

    # Примеры данных
    logger.info(f"\n📋 ПРИМЕРЫ ДАННЫХ (первые 5 строк):")
    for i, row in df.head(5).iterrows():
        logger.info(f"   Строка {i + 1}:")
        for col in df.columns:
            val = row[col]
            if pd.notna(val) and val:
                logger.info(f"      {col}: {val[:100]}..." if len(str(val)) > 100 else f"      {col}: {val}")

    return df


def check_tr_ts_files():
    """Проверяет файлы ТР ТС"""

    logger.info("\n" + "=" * 80)
    logger.info("📂 ПРОВЕРКА ФАЙЛОВ ТР ТС")
    logger.info("=" * 80)

    tr_ts_files = {
        "TR_TS_007": RAW_DATA_DIR / "tr_ts_007.docx",
        "TR_TS_017": RAW_DATA_DIR / "tr_ts_017.docx",
    }

    for name, path in tr_ts_files.items():
        if path.exists():
            logger.info(f"✅ {name}: {path.name} ({path.stat().st_size / 1024:.1f} KB)")

            # Пробуем прочитать
            try:
                text = read_docx(path)
                logger.info(f"   Символов: {len(text)}")
                logger.info(f"   Первые 200 символов: {text[:200]}...")
            except Exception as e:
                logger.error(f"   ❌ Ошибка чтения: {e}")
        else:
            logger.warning(f"⚠️  {name}: файл не найден ({path})")
            logger.info(f"   Ожидается файл: {path}")


def check_data_directory():
    """Проверяет структуру папок"""

    logger.info("\n" + "=" * 80)
    logger.info("📂 ПРОВЕРКА СТРУКТУРЫ ПАПОК")
    logger.info("=" * 80)

    dirs = [
        ("data/raw", RAW_DATA_DIR),
        ("data/processed", PROCESSED_DATA_DIR),
        ("data/rules", RULES_DIR),
    ]

    for name, path in dirs:
        if path.exists():
            files = list(path.glob("*"))
            logger.info(f"✅ {name}: {len(files)} файлов")
            for f in files[:5]:
                logger.info(f"   - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
            if len(files) > 5:
                logger.info(f"   ... и еще {len(files) - 5} файлов")
        else:
            logger.warning(f"⚠️  {name}: папка не существует")


def check_env():
    """Проверяет наличие .env файла"""

    logger.info("\n" + "=" * 80)
    logger.info("📂 ПРОВЕРКА .env")
    logger.info("=" * 80)

    env_file = Path(".env")
    if env_file.exists():
        logger.info(f"✅ .env файл найден: {env_file}")
        # Проверяем наличие ключа
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "DEEPSEEK_API_KEY=" in content:
                logger.info("✅ DEEPSEEK_API_KEY присутствует")
            else:
                logger.warning("⚠️  DEEPSEEK_API_KEY не найден в .env")
    else:
        logger.warning(f"⚠️  .env файл не найден")


if __name__ == "__main__":

    # Проверяем структуру папок
    check_data_directory()

    # Проверяем .env
    check_env()

    # Проверяем файлы ТР ТС
    check_tr_ts_files()

    # Проверяем Excel
    excel_files = list(RAW_DATA_DIR.glob("*.xlsx"))

    if not excel_files:
        logger.error("\n❌ В папке data/raw/ нет Excel-файлов с протоколами")
        logger.info("   Поместите файл с протоколами в data/raw/")
    else:
        logger.info(f"\n📂 Найдены Excel-файлы:")
        for f in excel_files:
            logger.info(f"   - {f.name}")

        # Проверяем первый найденный файл
        df = check_excel_data(excel_files[0])

        if df is not None:
            # Сохраняем информацию о структуре
            info_file = PROCESSED_DATA_DIR / "data_structure_info.txt"
            info_file.parent.mkdir(parents=True, exist_ok=True)

            with open(info_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ИНФОРМАЦИЯ О СТРУКТУРЕ ДАННЫХ\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Всего строк: {len(df)}\n")
                f.write(f"Всего колонок: {len(df.columns)}\n")
                f.write(f"Колонки: {list(df.columns)}\n\n")

                for col in df.columns:
                    unique_count = df[col].nunique()
                    null_count = df[col].isna().sum()
                    f.write(f"\nКолонка: {col}\n")
                    f.write(f"  Уникальных: {unique_count}\n")
                    f.write(f"  Пустых: {null_count} ({null_count / len(df) * 100:.1f}%)\n")

                    # Топ-10 значений
                    top_values = df[col].value_counts().head(10)
                    f.write(f"  Топ-10 значений:\n")
                    for val, count in top_values.items():
                        val_str = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
                        f.write(f"    {val_str} → {count}\n")

            logger.info(f"\n✅ Информация о структуре сохранена: {info_file}")

    logger.info("\n" + "=" * 80)
    logger.info("✅ ПРОВЕРКА ЗАВЕРШЕНА")
    logger.info("=" * 80)