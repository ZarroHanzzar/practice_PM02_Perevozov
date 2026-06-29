"""
Модуль эмуляции базы данных
Версия: 2.0.0
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date  # ← ИСПРАВЛЕНО
from models import Hotel, Room, Booking, BookingStatus


class Database:
    """Эмуляция базы данных (в памяти)"""
    
    def __init__(self):
        self.hotels: Dict[str, Hotel] = {}
        self.bookings: Dict[str, Booking] = {}
        self._id_counter = 0

    def generate_id(self) -> str:
        """Генерация уникального ID"""
        self._id_counter += 1
        return f"BKG-{self._id_counter:06d}"

    # === HOTEL CRUD ===
    
    def add_hotel(self, hotel: Hotel) -> bool:
        """Добавить отель"""
        if hotel.id in self.hotels:
            return False
        self.hotels[hotel.id] = hotel
        return True

    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """Получить отель по ID"""
        return self.hotels.get(hotel_id)

    def get_all_hotels(self) -> List[Hotel]:
        """Получить все отели"""
        return list(self.hotels.values())

    def update_hotel(self, hotel_id: str, data: Dict[str, Any]) -> bool:
        """Обновить отель"""
        hotel = self.get_hotel(hotel_id)
        if not hotel:
            return False
        for key, value in data.items():
            if hasattr(hotel, key) and key != "id" and key != "rooms":
                setattr(hotel, key, value)
        return True

    def delete_hotel(self, hotel_id: str) -> bool:
        """Удалить отель"""
        if hotel_id not in self.hotels:
            return False
        del self.hotels[hotel_id]
        return True

    # === ROOM CRUD ===
    
    def add_room(self, room: Room) -> bool:
        """Добавить номер"""
        hotel = self.get_hotel(room.hotel_id)
        if not hotel:
            return False
        for existing_room in hotel.rooms:
            if existing_room.id == room.id:
                return False
        hotel.rooms.append(room)
        return True

    def get_room(self, hotel_id: str, room_id: str) -> Optional[Room]:
        """Получить номер"""
        hotel = self.get_hotel(hotel_id)
        if not hotel:
            return None
        for room in hotel.rooms:
            if room.id == room_id:
                return room
        return None

    def get_available_rooms(self, hotel_id: str, check_in: date, check_out: date) -> List[Room]:
        """Получить доступные номера на даты"""
        hotel = self.get_hotel(hotel_id)
        if not hotel:
            return []
        
        busy_room_ids = set()
        for booking in self.bookings.values():
            if booking.hotel_id != hotel_id:
                continue
            if booking.status in [BookingStatus.CANCELLED, BookingStatus.PENDING]:
                continue
            if booking.check_in < check_out and booking.check_out > check_in:
                busy_room_ids.add(booking.room_id)
        
        available = []
        for room in hotel.rooms:
            if room.id not in busy_room_ids and room.is_available:
                available.append(room)
        return available

    # === BOOKING CRUD ===
    
    def create_booking(self, booking: Booking) -> Optional[Booking]:
        """Создать бронирование"""
        available_rooms = self.get_available_rooms(
            booking.hotel_id,
            booking.check_in,
            booking.check_out
        )
        if booking.room_id not in [r.id for r in available_rooms]:
            return None
        
        booking.id = self.generate_id()
        booking.created_at = datetime.now().isoformat()
        self.bookings[booking.id] = booking
        return booking

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Получить бронирование"""
        return self.bookings.get(booking_id)

    def get_bookings_by_hotel(self, hotel_id: str) -> List[Booking]:
        """Получить все бронирования отеля"""
        return [b for b in self.bookings.values() if b.hotel_id == hotel_id]

    def get_bookings_by_guest(self, guest_email: str) -> List[Booking]:
        """Получить бронирования гостя"""
        return [b for b in self.bookings.values() if b.guest_email == guest_email]

    def cancel_booking(self, booking_id: str) -> bool:
        """Отменить бронирование"""
        booking = self.get_booking(booking_id)
        if not booking:
            return False
        booking.status = BookingStatus.CANCELLED
        return True

    def check_in(self, booking_id: str) -> bool:
        """Заселить гостя"""
        booking = self.get_booking(booking_id)
        if not booking or booking.status != BookingStatus.CONFIRMED:
            return False
        booking.status = BookingStatus.CHECKED_IN
        return True

    def check_out(self, booking_id: str) -> bool:
        """Выселить гостя"""
        booking = self.get_booking(booking_id)
        if not booking or booking.status != BookingStatus.CHECKED_IN:
            return False
        booking.status = BookingStatus.CHECKED_OUT
        return True

    # === DATA IMPORT/EXPORT ===
    
    def load_from_file(self, filename: str) -> bool:
        """Загрузить данные из JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for hotel_data in data.get("hotels", []):
                hotel = Hotel.from_dict(hotel_data)
                self.add_hotel(hotel)
            
            for booking_data in data.get("bookings", []):
                booking = Booking.from_dict(booking_data)
                self.bookings[booking.id] = booking
            
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False

    def save_to_file(self, filename: str) -> bool:
        """Сохранить данные в JSON"""
        try:
            data = {
                "hotels": [h.to_dict() for h in self.get_all_hotels()],
                "bookings": [b.to_dict() for b in self.bookings.values()]
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False