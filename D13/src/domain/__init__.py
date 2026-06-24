# src/domain/__init__.py
from src.domain.models import Hotel, Room, Booking, BookingStatus, DailyBookingQuota, CircuitBreakerState
from src.domain.exceptions import (
    DomainError,
    RoomNotFoundError,
    RoomNotAvailableError,
    BookingNotFoundError,
    BookingConflictError,
    InvalidDatesError,
    HotelNotFoundError,
    QuotaExceededError,
    CircuitBreakerOpenError
)

__all__ = [
    'Hotel',
    'Room',
    'Booking',
    'BookingStatus',
    'DailyBookingQuota',
    'CircuitBreakerState',
    'DomainError',
    'RoomNotFoundError',
    'RoomNotAvailableError',
    'BookingNotFoundError',
    'BookingConflictError',
    'InvalidDatesError',
    'HotelNotFoundError',
    'QuotaExceededError',
    'CircuitBreakerOpenError'
]