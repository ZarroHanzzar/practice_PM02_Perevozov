# src/config.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Конфигурация приложения"""
    daily_booking_limit: int = 3
    circuit_breaker_timeout_seconds: int = 60
    circuit_breaker_failure_threshold: int = 3
    max_booking_days: int = 30
    min_booking_days: int = 1
    
    # Сезонные коэффициенты
    seasonal_coefficients: dict = None
    
    def __post_init__(self):
        if self.seasonal_coefficients is None:
            self.seasonal_coefficients = {
                6: 1.2,
                7: 1.5,
                8: 1.5,
                12: 1.3,
                1: 1.1,
            }


# Глобальный экземпляр конфигурации
config = Config()