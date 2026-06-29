"""
Сервис управления бронированиями
Версия: 2.0.0
"""

from typing import List, Optional
from datetime import date
from models import Booking, BookingStatus
from database import Database
from hotel_service import HotelService


class BookingService:
    """Сервис для работы с бронированиями"""
    
    def __init__(self, db: Database, hotel_service: HotelService):
        self.db = db
        self.hotel_service = hotel_service

    def create_booking(self, hotel_id: str, room_id: str, guest_name: str,
                       guest_email: str, guest_phone: str,
                       check_in: date, check_out: date) -> Optional[Booking]:
        """Создать бронирование"""
        if check_in >= check_out:
            print("Ошибка: дата заезда должна быть раньше даты выезда")
            return None
        
        hotel = self.hotel_service.get_hotel(hotel_id)
        if not hotel:
            print(f"Ошибка: отель {hotel_id} не найден")
            return None
        
        room = self.hotel_service.get_room(hotel_id, room_id)
        if not room:
            print(f"Ошибка: номер {room_id} не найден в отеле {hotel_id}")
            return None
        
        nights = (check_out - check_in).days
        if nights <= 0:
            print("Ошибка: количество ночей должно быть больше 0")
            return None
        
        total_price = room.price_per_night * nights
        
        booking = Booking(
            id="",
            hotel_id=hotel_id,
            room_id=room_id,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            status=BookingStatus.CONFIRMED
        )
        
        result = self.db.create_booking(booking)
        if result:
            print(f"✅ Бронирование создано: {result.id}")
            print(f"   Гость: {guest_name}")
            print(f"   Стоимость: {total_price} руб.")
        else:
            print(f"❌ Номер {room_id} занят на указанные даты")
        
        return result

    def cancel_booking(self, booking_id: str) -> bool:
        """Отменить бронирование"""
        booking = self.db.get_booking(booking_id)
        if not booking:
            print(f"❌ Бронирование {booking_id} не найдено")
            return False
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.CHECKED_OUT]:
            print(f"❌ Бронирование уже {booking.status.value}")
            return False
        
        if self.db.cancel_booking(booking_id):
            print(f"✅ Бронирование {booking_id} отменено")
            return True
        return False

    def check_in(self, booking_id: str) -> bool:
        """Заселение"""
        booking = self.db.get_booking(booking_id)
        if not booking:
            print(f"❌ Бронирование {booking_id} не найдено")
            return False
        
        if booking.status != BookingStatus.CONFIRMED:
            print(f"❌ Невозможно заселить: статус {booking.status.value}")
            return False
        
        if self.db.check_in(booking_id):
            print(f"✅ Гость {booking.guest_name} заселен")
            return True
        return False

    def check_out(self, booking_id: str) -> bool:
        """Выселение"""
        booking = self.db.get_booking(booking_id)
        if not booking:
            print(f"❌ Бронирование {booking_id} не найдено")
            return False
        
        if booking.status != BookingStatus.CHECKED_IN:
            print(f"❌ Невозможно выселить: статус {booking.status.value}")
            return False
        
        if self.db.check_out(booking_id):
            print(f"✅ Гость {booking.guest_name} выселен")
            return True
        return False

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Получить бронирование"""
        return self.db.get_booking(booking_id)

    def get_bookings_by_hotel(self, hotel_id: str) -> List[Booking]:
        """Получить все бронирования отеля"""
        return self.db.get_bookings_by_hotel(hotel_id)

    def get_bookings_by_guest(self, guest_email: str) -> List[Booking]:
        """Получить бронирования гостя"""
        return self.db.get_bookings_by_guest(guest_email)

    def get_guest_history(self, guest_email: str) -> List[Booking]:
        """Получить историю бронирований гостя"""
        return sorted(
            self.db.get_bookings_by_guest(guest_email),
            key=lambda b: b.check_in,
            reverse=True
        )

    def calculate_revenue(self, hotel_id: str, start_date: date, end_date: date) -> float:
        """Рассчитать выручку отеля за период"""
        bookings = self.db.get_bookings_by_hotel(hotel_id)
        revenue = 0.0
        for booking in bookings:
            if booking.status in [BookingStatus.CANCELLED, BookingStatus.PENDING]:
                continue
            if booking.check_in < end_date and booking.check_out > start_date:
                revenue += booking.total_price
        return revenue