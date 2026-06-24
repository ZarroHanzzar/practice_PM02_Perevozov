# src/services/hotel_service.py
from typing import List, Optional
from src.domain.models import Hotel, Room
from src.domain.exceptions import HotelNotFoundError
from src.dto.hotel_dto import HotelCreateDTO, HotelResponseDTO, HotelUpdateDTO
from uow.unit_of_work import UnitOfWork


class HotelService:
    """Сервис для управления отелями"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.hotel_repo = uow.hotels
        self.room_repo = uow.rooms
    
    def create(self, dto: HotelCreateDTO) -> HotelResponseDTO:
        """Создать новый отель"""
        hotel = Hotel(
            id=None,
            name=dto.name,
            address=dto.address,
            phone=dto.phone,
            rating=dto.rating
        )
        saved = self.hotel_repo.add(hotel)
        self.uow.commit()
        return HotelResponseDTO(
            id=saved.id,
            name=saved.name,
            address=saved.address,
            phone=saved.phone,
            rating=saved.rating,
            created_at=saved.created_at
        )
    
    def get_by_id(self, hotel_id: int) -> Optional[HotelResponseDTO]:
        """Получить отель по ID"""
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель {hotel_id} не найден")
        return HotelResponseDTO(
            id=hotel.id,
            name=hotel.name,
            address=hotel.address,
            phone=hotel.phone,
            rating=hotel.rating,
            created_at=hotel.created_at
        )
    
    def get_all(self, **filters) -> List[HotelResponseDTO]:
        """Получить все отели с фильтрацией"""
        hotels = self.hotel_repo.get_all(**filters)
        return [
            HotelResponseDTO(
                id=h.id,
                name=h.name,
                address=h.address,
                phone=h.phone,
                rating=h.rating,
                created_at=h.created_at
            )
            for h in hotels
        ]
    
    def update(self, hotel_id: int, dto: HotelUpdateDTO) -> HotelResponseDTO:
        """Обновить отель"""
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель {hotel_id} не найден")
        
        if dto.name is not None:
            hotel.name = dto.name
        if dto.address is not None:
            hotel.address = dto.address
        if dto.phone is not None:
            hotel.phone = dto.phone
        if dto.rating is not None:
            hotel.rating = dto.rating
        
        updated = self.hotel_repo.update(hotel)
        self.uow.commit()
        
        return HotelResponseDTO(
            id=updated.id,
            name=updated.name,
            address=updated.address,
            phone=updated.phone,
            rating=updated.rating,
            created_at=updated.created_at
        )
    
    def delete(self, hotel_id: int) -> bool:
        """Удалить отель"""
        if not self.hotel_repo.get_by_id(hotel_id):
            raise HotelNotFoundError(f"Отель {hotel_id} не найден")
        result = self.hotel_repo.delete(hotel_id)
        self.uow.commit()
        return result