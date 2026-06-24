# src/dto/__init__.py
from src.dto.booking_dto import (
    BookingCreateDTO,
    BookingResponseDTO,
    BookingUpdateDTO,
    QuotaResponseDTO
)
from src.dto.hotel_dto import HotelCreateDTO, HotelResponseDTO, HotelUpdateDTO
from src.dto.room_dto import RoomCreateDTO, RoomResponseDTO, RoomUpdateDTO

__all__ = [
    'BookingCreateDTO',
    'BookingResponseDTO',
    'BookingUpdateDTO',
    'QuotaResponseDTO',
    'HotelCreateDTO',
    'HotelResponseDTO',
    'HotelUpdateDTO',
    'RoomCreateDTO',
    'RoomResponseDTO',
    'RoomUpdateDTO'
]