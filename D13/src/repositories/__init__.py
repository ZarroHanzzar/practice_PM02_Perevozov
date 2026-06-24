# src/repositories/__init__.py
from src.repositories.base import BaseRepository
from src.repositories.hotel_repo import HotelRepository
from src.repositories.room_repo import RoomRepository
from src.repositories.booking_repo import BookingRepository
from src.repositories.quota_repo import QuotaRepository

__all__ = [
    'BaseRepository',
    'HotelRepository',
    'RoomRepository',
    'BookingRepository',
    'QuotaRepository'
]