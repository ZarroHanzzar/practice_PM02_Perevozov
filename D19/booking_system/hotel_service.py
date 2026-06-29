"""
Сервис управления отелями
Версия: 2.0.0
"""

from typing import List, Optional, Dict, Any
from datetime import date
from models import Hotel, Room
from database import Database


class HotelService:
    """Сервис для работы с отелями"""
    
    def __init__(self, db: Database):
        self.db = db

    def create_hotel(self, name: str, address: str, phone: str, email: str) -> Optional[Hotel]:
        """Создать новый отель"""
        hotel_id = f"HOTEL-{len(self.db.get_all_hotels()) + 1:04d}"
        hotel = Hotel(
            id=hotel_id,
            name=name,
            address=address,
            phone=phone,
            email=email
        )
        if self.db.add_hotel(hotel):
            return hotel
        return None

    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """Получить отель по ID"""
        return self.db.get_hotel(hotel_id)

    def get_all_hotels(self) -> List[Hotel]:
        """Получить все отели"""
        return self.db.get_all_hotels()

    def update_hotel(self, hotel_id: str, data: Dict[str, Any]) -> bool:
        """Обновить отель"""
        return self.db.update_hotel(hotel_id, data)

    def delete_hotel(self, hotel_id: str) -> bool:
        """Удалить отель"""
        return self.db.delete_hotel(hotel_id)

    def add_room(self, hotel_id: str, room_id: str, price_per_night: float, 
                 capacity: int = 2, floor: int = None, room_type: str = "standard") -> Optional[Room]:
        """Добавить номер в отель"""
        hotel = self.db.get_hotel(hotel_id)
        if not hotel:
            return None
        
        room = Room(
            id=room_id,
            hotel_id=hotel_id,
            price_per_night=price_per_night,
            capacity=capacity,
            floor=floor,
            room_type=room_type
        )
        if self.db.add_room(room):
            return room
        return None

    def get_available_rooms(self, hotel_id: str, check_in: date, check_out: date) -> List[Room]:
        """Получить доступные номера"""
        return self.db.get_available_rooms(hotel_id, check_in, check_out)

    def get_room(self, hotel_id: str, room_id: str) -> Optional[Room]:
        """Получить номер"""
        return self.db.get_room(hotel_id, room_id)

    def search_hotels(self, query: str) -> List[Hotel]:
        """Поиск отелей по имени или адресу"""
        query_lower = query.lower()
        results = []
        for hotel in self.db.get_all_hotels():
            if query_lower in hotel.name.lower() or query_lower in hotel.address.lower():
                results.append(hotel)
        return results