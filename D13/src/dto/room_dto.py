# src/dto/room_dto.py
from pydantic import BaseModel
from typing import Optional


class RoomCreateDTO(BaseModel):
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    room_type: str = "standard"


class RoomResponseDTO(BaseModel):
    id: int
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool
    room_type: str


class RoomUpdateDTO(BaseModel):
    number: Optional[str] = None
    capacity: Optional[int] = None
    price_per_night: Optional[float] = None
    is_active: Optional[bool] = None
    room_type: Optional[str] = None