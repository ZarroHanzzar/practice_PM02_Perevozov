"""
Модуль конфигурации
Версия: 2.0.0
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Конфигурация системы"""
    
    # Общие настройки
    APP_NAME: str = "Система управления бронированиями"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Настройки базы данных
    DB_TYPE: str = "memory"
    DB_FILE: str = "data.json"
    
    # Настройки API
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "booking.log"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Загрузить конфигурацию из переменных окружения"""
        return cls(
            DEBUG=os.getenv("DEBUG", "True").lower() == "true",
            DB_FILE=os.getenv("DB_FILE", "data.json"),
            API_HOST=os.getenv("API_HOST", "localhost"),
            API_PORT=int(os.getenv("API_PORT", "8000")),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO")
        )


# Глобальный экземпляр конфигурации
config = Config()