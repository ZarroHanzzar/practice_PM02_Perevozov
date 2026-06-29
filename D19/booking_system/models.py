"""
Модуль моделей данных для системы управления бронированиями
Версия: 2.0.0
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict, Any
from enum import Enum


class BookingStatus(Enum):
    """Статусы бронирования"""
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    PENDING = "pending"


@dataclass
class Room:
    """Модель номера"""
    id: str
    hotel_id: str
    price_per_night: float
    capacity: int = 2
    is_available: bool = True
    floor: Optional[int] = None
    room_type: str = "standard"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hotel_id": self.hotel_id,
            "price_per_night": self.price_per_night,
            "capacity": self.capacity,
            "is_available": self.is_available,
            "floor": self.floor,
            "room_type": self.room_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Room':
        return cls(
            id=data["id"],
            hotel_id=data["hotel_id"],
            price_per_night=data["price_per_night"],
            capacity=data.get("capacity", 2),
            is_available=data.get("is_available", True),
            floor=data.get("floor"),
            room_type=data.get("room_type", "standard")
        )


@dataclass
class Hotel:
    """Модель отеля"""
    id: str
    name: str
    address: str
    phone: str
    email: str
    rating: float = 0.0
    rooms: List[Room] = None

    def __post_init__(self):
        if self.rooms is None:
            self.rooms = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "rating": self.rating,
            "rooms": [room.to_dict() for room in self.rooms]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hotel':
        hotel = cls(
            id=data["id"],
            name=data["name"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            rating=data.get("rating", 0.0)
        )
        for room_data in data.get("rooms", []):
            hotel.rooms.append(Room.from_dict(room_data))
        return hotel


@dataclass
class Booking:
    """Модель бронирования"""
    id: str
    hotel_id: str
    room_id: str
    guest_name: str
    guest_email: str
    guest_phone: str
    check_in: date
    check_out: date
    total_price: float
    status: BookingStatus = BookingStatus.PENDING
    created_at: Optional[str] = None

    def get_nights(self) -> int:
        """Рассчитать количество ночей"""
        return (self.check_out - self.check_in).days

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hotel_id": self.hotel_id,
            "room_id": self.room_id,
            "guest_name": self.guest_name,
            "guest_email": self.guest_email,
            "guest_phone": self.guest_phone,
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "total_price": self.total_price,
            "status": self.status.value,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Booking':
        return cls(
            id=data["id"],
            hotel_id=data["hotel_id"],
            room_id=data["room_id"],
            guest_name=data["guest_name"],
            guest_email=data["guest_email"],
            guest_phone=data["guest_phone"],
            check_in=date.fromisoformat(data["check_in"]),
            check_out=date.fromisoformat(data["check_out"]),
            total_price=data["total_price"],
            status=BookingStatus(data.get("status", "pending")),
            created_at=data.get("created_at")
        )