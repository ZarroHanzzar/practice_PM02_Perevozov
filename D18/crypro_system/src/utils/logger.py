# src/utils/logger.py
"""
Logging utilities
"""
import logging
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """Логгер для приложения"""
    
    _instance: Optional['Logger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        """Настройка логгера"""
        self.logger = logging.getLogger('crypto_system')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler для консоли
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Формат
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # Handler для файла
        file_handler = logging.FileHandler('crypto_system.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        self.logger.critical(message)


def get_logger() -> Logger:
    """Получение экземпляра логгера"""
    return Logger()