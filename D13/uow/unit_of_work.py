# src/uow/unit_of_work.py
from contextlib import contextmanager

from src.repositories.hotel_repo import HotelRepository
from src.repositories.room_repo import RoomRepository
from src.repositories.booking_repo import BookingRepository
from src.repositories.quota_repo import QuotaRepository


class UnitOfWork:
    """Unit of Work для управления транзакциями"""
    
    def __init__(self):
        self._hotel_repo = HotelRepository()
        self._room_repo = RoomRepository()
        self._booking_repo = BookingRepository()
        self._quota_repo = QuotaRepository()
        self._committed = False
    
    @property
    def hotels(self) -> HotelRepository:
        return self._hotel_repo
    
    @property
    def rooms(self) -> RoomRepository:
        return self._room_repo
    
    @property
    def bookings(self) -> BookingRepository:
        return self._booking_repo
    
    @property
    def quotas(self) -> QuotaRepository:
        return self._quota_repo
    
    def commit(self) -> None:
        self._committed = True
    
    def rollback(self) -> None:
        self._committed = False
    
    @contextmanager
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        elif not self._committed:
            self.commit()