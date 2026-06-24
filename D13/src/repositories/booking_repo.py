# src/repositories/booking_repo.py
from typing import List, Optional
from datetime import date
from src.domain.models import Booking, BookingStatus
from src.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    def __init__(self):
        self._storage: dict[int, Booking] = {}
        self._next_id = 1
    
    def get_by_id(self, id: int) -> Optional[Booking]:
        return self._storage.get(id)
    
    def get_all(self, **filters) -> List[Booking]:
        result = list(self._storage.values())
        
        if 'room_id' in filters:
            result = [b for b in result if b.room_id == filters['room_id']]
        if 'status' in filters:
            result = [b for b in result if b.status == filters['status']]
        if 'guest_email' in filters:
            result = [b for b in result if b.guest_email == filters['guest_email']]
        
        return result
    
    def get_by_room_and_dates(
        self,
        room_id: int,
        check_in: date,
        check_out: date
    ) -> List[Booking]:
        """Найти бронирования для номера в указанном диапазоне"""
        result = []
        for booking in self._storage.values():
            if booking.room_id != room_id:
                continue
            if booking.status == BookingStatus.CANCELLED:
                continue
            
            # Пересечение интервалов
            if booking.check_in < check_out and booking.check_out > check_in:
                result.append(booking)
        
        return result
    
    def get_by_guest_email(self, guest_email: str) -> List[Booking]:
        """Получить все бронирования гостя"""
        return [b for b in self._storage.values() if b.guest_email == guest_email]
    
    def get_active_by_guest_email(self, guest_email: str) -> List[Booking]:
        """Получить активные бронирования гостя"""
        return [
            b for b in self._storage.values()
            if b.guest_email == guest_email and b.status not in (
                BookingStatus.CANCELLED,
                BookingStatus.CHECKED_OUT
            )
        ]
    
    def add(self, booking: Booking) -> Booking:
        booking.id = self._next_id
        self._storage[booking.id] = booking
        self._next_id += 1
        return booking
    
    def update(self, booking: Booking) -> Booking:
        if booking.id not in self._storage:
            raise ValueError(f"Booking with id {booking.id} not found")
        self._storage[booking.id] = booking
        return booking
    
    def delete(self, id: int) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False