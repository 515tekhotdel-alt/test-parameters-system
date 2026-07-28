"""
Клиент для работы с DeepSeek API
"""

import requests
import json
from typing import Optional

from src.utils.logger import logger
from config.settings import DEEPSEEK_API_URL, DEEPSEEK_MODEL


class DeepSeekClient:
    """Клиент для взаимодействия с DeepSeek API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = DEEPSEEK_API_URL
        self.model = DEEPSEEK_MODEL

    def chat(self, prompt: str, max_tokens: int = 8000, temperature: float = 0.3) -> str:
        """
        Отправляет запрос к DeepSeek API

        Args:
            prompt: Текст запроса
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (0.0-1.0)

        Returns:
            str: Ответ от API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Ты — эксперт по техническому регулированию в области легкой промышленности. Отвечай структурированно, только в формате JSON. Используй русский язык."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        try:
            logger.info(f"📤 Отправка запроса в DeepSeek (модель: {self.model})")
            logger.info(f"   Длина промпта: {len(prompt)} символов")

            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=180  # 3 минуты на ответ
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info(f"✅ Получен ответ ({len(content)} символов)")
                return content
            else:
                logger.error(f"❌ Ошибка API: {response.status_code}")
                logger.error(response.text)
                return f'{{"error": "API error: {response.status_code}"}}'

        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут запроса к DeepSeek API (180 сек)")
            return '{"error": "timeout"}'
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            return f'{{"error": "{str(e)}"}}'