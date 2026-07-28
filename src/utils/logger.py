"""
Настройка логирования
"""

import sys
from pathlib import Path
from loguru import logger

from config.settings import LOG_LEVEL, LOG_FILE


def setup_logger():
    """Настройка логгера"""

    # Удаляем стандартный обработчик
    logger.remove()

    # Добавляем вывод в консоль
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        colorize=True
    )

    # Создаем папку для логов если её нет
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Добавляем вывод в файл
    logger.add(
        LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=LOG_LEVEL,
        rotation="10 MB",
        retention="30 days"
    )

    return logger


# Создаем логгер при импорте
logger = setup_logger()