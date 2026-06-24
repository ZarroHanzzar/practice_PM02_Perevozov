# src/domain/exceptions.py
class DomainError(Exception):
    """Базовое исключение домена"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class RoomNotFoundError(DomainError):
    """Номер не найден"""
    pass


class RoomNotAvailableError(DomainError):
    """Номер недоступен"""
    pass


class BookingNotFoundError(DomainError):
    """Бронирование не найдено"""
    pass


class BookingConflictError(DomainError):
    """Пересечение бронирований на один номер"""
    pass


class InvalidDatesError(DomainError):
    """Некорректные даты"""
    pass


class HotelNotFoundError(DomainError):
    """Отель не найден"""
    pass


class QuotaExceededError(DomainError):
    """Превышение квоты на бронирования"""
    pass


class CircuitBreakerOpenError(DomainError):
    """Circuit Breaker открыт - запросы временно блокируются"""
    pass