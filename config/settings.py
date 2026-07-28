"""
Конфигурация приложения
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env только если файл существует
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Корень проекта
BASE_DIR = Path(__file__).parent.parent

# Данные
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RULES_DIR = DATA_DIR / "rules"

# Протоколы
PROTOCOLS_DIR = RAW_DATA_DIR / "protocols"

# Логи
LOGS_DIR = BASE_DIR / "logs"

# DeepSeek (безопасное получение ключа)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1"

# Пороги частотности
MANDATORY_THRESHOLD = 0.90
FREQUENT_THRESHOLD = 0.50

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# Streamlit
STREAMLIT_THEME = "dark"