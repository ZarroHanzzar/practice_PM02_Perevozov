# tests/test_booking_service.py
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from src.services.booking_service import BookingService
from src.services.circuit_breaker import CircuitBreakerState
from src.domain.models import Room, Booking, BookingStatus
from src.domain.exceptions import (
    QuotaExceededError,
    CircuitBreakerOpenError,
    RoomNotFoundError,
    BookingConflictError,
    BookingNotFoundError
)
from src.dto.booking_dto import BookingCreateDTO


class TestBookingService:
    """Тесты для BookingService с Circuit Breaker"""
    
    def test_create_booking_within_quota(self, booking_service, mock_uow, sample_booking_dto, sample_room):
        """Тест создания бронирования в рамках квоты"""
        # Arrange
        mock_uow.rooms.get_by_id.return_value = sample_room
        mock_uow.bookings.get_by_room_and_dates.return_value = []
        mock_uow.quotas.get_by_email_and_date.return_value = None
        
        mock_saved = Booking(
            id=1,
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            total_price=500.0,
            status=BookingStatus.PENDING
        )
        mock_uow.bookings.add.return_value = mock_saved
        
        # Act
        result = booking_service.create(sample_booking_dto)
        
        # Assert
        assert result.id == 1
        mock_uow.quotas.increment_booking_count.assert_called_once()
        mock_uow.commit.assert_called_once()
    
    def test_create_booking_exceeds_quota(self, booking_service, mock_uow, sample_booking_dto):
        """Тест: бронирование превышает квоту"""
        # Arrange
        mock_quota = Mock()
        mock_quota.count = 3
        mock_uow.quotas.get_by_email_and_date.return_value = mock_quota
        
        # Act & Assert
        with pytest.raises(QuotaExceededError) as exc_info:
            booking_service.create(sample_booking_dto)
        
        assert "Превышен лимит бронирований" in str(exc_info.value)
        assert exc_info.value.details['today_count'] == 3
        mock_uow.bookings.add.assert_not_called()
    
    def test_circuit_breaker_opens_after_failures(self, booking_service, mock_uow, sample_booking_dto):
        """Тест: Circuit Breaker открывается после нескольких неудачных попыток"""
        # Arrange
        mock_quota = Mock()
        mock_quota.count = 3
        mock_uow.quotas.get_by_email_and_date.return_value = mock_quota
        mock_uow.rooms.get_by_id.return_value = Mock()
        mock_uow.bookings.get_by_room_and_dates.return_value = []
        
        # Act - Первые попытки превышают лимит
        for _ in range(3):
            with pytest.raises(QuotaExceededError):
                booking_service.create(sample_booking_dto)
        
        # Проверяем состояние Circuit Breaker
        breaker = booking_service._get_breaker("john@example.com")
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Следующая попытка должна быть заблокирована
        with pytest.raises(CircuitBreakerOpenError):
            booking_service.create(sample_booking_dto)
    
    def test_circuit_breaker_recovers_after_timeout(self, booking_service, mock_uow, sample_booking_dto, sample_room):
        """Тест: Circuit Breaker восстанавливается после таймаута"""
        # Arrange
        mock_quota = Mock()
        mock_quota.count = 3
        mock_uow.quotas.get_by_email_and_date.return_value = mock_quota
        mock_uow.rooms.get_by_id.return_value = sample_room
        mock_uow.bookings.get_by_room_and_dates.return_value = []
        
        # Открываем Circuit Breaker
        for _ in range(3):
            with pytest.raises(QuotaExceededError):
                booking_service.create(sample_booking_dto)
        
        breaker = booking_service._get_breaker("john@example.com")
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Act - Имитируем прохождение времени и сброс квоты
        with patch('src.services.booking_service.date') as mock_date:
            mock_date.today.return_value = date(2026, 6, 16)
            mock_uow.quotas.get_by_email_and_date.return_value = None
            
            mock_saved = Booking(
                id=1,
                room_id=1,
                guest_name="John Doe",
                guest_email="john@example.com",
                check_in=date(2026, 6, 15),
                check_out=date(2026, 6, 20),
                total_price=500.0,
                status=BookingStatus.PENDING
            )
            mock_uow.bookings.add.return_value = mock_saved
            
            # Имитируем прохождение времени для Circuit Breaker
            breaker.next_attempt_time = datetime.now()
            
            # Act
            result = booking_service.create(sample_booking_dto)
            
            # Assert
            assert result.id == 1
            assert breaker.state == CircuitBreakerState.CLOSED
    
    def test_get_quota_status(self, booking_service, mock_uow):
        """Тест получения статуса квоты"""
        # Arrange
        today = date.today()
        mock_quota = Mock()
        mock_quota.count = 2
        mock_uow.quotas.get_by_email_and_date.return_value = mock_quota
        
        # Act
        status = booking_service.get_quota_status("john@example.com")
        
        # Assert
        assert status.guest_email == "john@example.com"
        assert status.today_bookings == 2
        assert status.max_limit == 3
        assert status.remaining == 1
        assert status.can_book is True
    
    def test_cancel_booking_decreases_quota(self, booking_service, mock_uow, sample_booking):
        """Тест: отмена бронирования уменьшает счетчик квоты"""
        # Arrange
        mock_uow.bookings.get_by_id.return_value = sample_booking
        
        mock_quota = Mock()
        mock_quota.count = 2
        mock_uow.quotas.get_by_email_and_date.return_value = mock_quota
        
        # Act
        result = booking_service.cancel(1)
        
        # Assert
        assert result is True
        assert sample_booking.status == BookingStatus.CANCELLED
        mock_uow.quotas.decrement_booking_count.assert_called_once()
        mock_uow.commit.assert_called_once()
    
    def test_cancel_booking_not_found(self, booking_service, mock_uow):
        """Тест: отмена несуществующего бронирования"""
        # Arrange
        mock_uow.bookings.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(BookingNotFoundError):
            booking_service.cancel(999)
    
    def test_create_booking_room_not_found(self, booking_service, mock_uow, sample_booking_dto):
        """Тест: создание бронирования для несуществующего номера"""
        # Arrange
        mock_uow.rooms.get_by_id.return_value = None
        mock_uow.quotas.get_by_email_and_date.return_value = None
        
        # Act & Assert
        with pytest.raises(RoomNotFoundError):
            booking_service.create(sample_booking_dto)
    
    def test_create_booking_conflict(self, booking_service, mock_uow, sample_booking_dto, sample_room):
        """Тест: создание бронирования с пересечением дат"""
        # Arrange
        mock_uow.rooms.get_by_id.return_value = sample_room
        mock_uow.quotas.get_by_email_and_date.return_value = None
        
        existing_booking = Booking(
            id=5,
            room_id=1,
            guest_name="Other",
            guest_email="other@example.com",
            check_in=date(2026, 6, 16),
            check_out=date(2026, 6, 18),
            total_price=200.0,
            status=BookingStatus.CONFIRMED
        )
        mock_uow.bookings.get_by_room_and_dates.return_value = [existing_booking]
        
        # Act & Assert
        with pytest.raises(BookingConflictError):
            booking_service.create(sample_booking_dto)
    
    def test_reset_breaker(self, booking_service):
        """Тест сброса Circuit Breaker"""
        # Arrange
        breaker = booking_service._get_breaker("john@example.com")
        breaker.state = CircuitBreakerState.OPEN
        
        # Act
        booking_service.reset_breaker("john@example.com")
        
        # Assert
        assert breaker.state == CircuitBreakerState.CLOSED
    
    def test_get_breaker_status(self, booking_service):
        """Тест получения статуса Circuit Breaker"""
        # Arrange
        breaker = booking_service._get_breaker("test@example.com")
        
        # Act
        status = booking_service.get_breaker_status("test@example.com")
        
        # Assert
        assert status['email'] == "test@example.com"
        assert status['state'] == "closed"