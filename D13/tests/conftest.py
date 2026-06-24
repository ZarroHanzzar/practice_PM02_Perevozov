# tests/conftest.py
import pytest
from datetime import date
from unittest.mock import Mock

from uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.circuit_breaker import CircuitBreakerRegistry
from src.services.booking_service import BookingService
from src.domain.models import Room, Booking, BookingStatus


@pytest.fixture
def mock_uow():
    """Фикстура для мока UnitOfWork"""
    uow = Mock(spec=UnitOfWork)
    uow.bookings = Mock()
    uow.rooms = Mock()
    uow.quotas = Mock()
    uow.commit = Mock()
    return uow


@pytest.fixture
def pricing_service():
    """Фикстура для PricingService"""
    return PricingService()


@pytest.fixture
def breaker_registry():
    """Фикстура для CircuitBreakerRegistry"""
    return CircuitBreakerRegistry()


@pytest.fixture
def booking_service(mock_uow, pricing_service, breaker_registry):
    """Фикстура для BookingService"""
    return BookingService(
        uow=mock_uow,
        pricing_service=pricing_service,
        breaker_registry=breaker_registry,
        daily_limit=3
    )


@pytest.fixture
def sample_room():
    """Фикстура с примером номера"""
    return Room(
        id=1,
        hotel_id=1,
        number="101",
        capacity=2,
        price_per_night=100.0,
        is_active=True,
        room_type="standard"
    )


@pytest.fixture
def sample_booking():
    """Фикстура с примером бронирования"""
    return Booking(
        id=1,
        room_id=1,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20),
        total_price=500.0,
        status=BookingStatus.PENDING
    )


@pytest.fixture
def sample_booking_dto():
    """Фикстура с DTO для создания бронирования"""
    from src.dto.booking_dto import BookingCreateDTO
    return BookingCreateDTO(
        room_id=1,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20)
    )