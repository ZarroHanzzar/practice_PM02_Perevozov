# src/dto/hotel_dto.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HotelCreateDTO(BaseModel):
    name: str
    address: str
    phone: str
    rating: float = 0.0


class HotelResponseDTO(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    rating: float
    created_at: datetime


class HotelUpdateDTO(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None