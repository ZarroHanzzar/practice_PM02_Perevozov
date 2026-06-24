# src/domain/models.py
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional, Dict, List


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class CircuitBreakerState(Enum):
    CLOSED = "closed"          # Нормальная работа
    OPEN = "open"              # Лимит превышен, запросы блокируются
    HALF_OPEN = "half_open"    # Проверка восстановления


@dataclass
class Hotel:
    id: Optional[int]
    name: str
    address: str
    phone: str
    rating: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Room:
    id: Optional[int]
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool = True
    room_type: str = "standard"


@dataclass
class Booking:
    id: Optional[int]
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    total_price: float
    status: BookingStatus = BookingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None


@dataclass
class DailyBookingQuota:
    """Сущность для отслеживания квот пользователя"""
    id: Optional[int]
    guest_email: str
    booking_date: date
    count: int = 0
    limit: int = 3
    last_updated: datetime = field(default_factory=datetime.now)