# src/services/booking_service.py
from datetime import date, datetime
from typing import List, Optional
from src.domain.models import Booking, BookingStatus
from src.domain.exceptions import (
    RoomNotFoundError,
    BookingConflictError,
    BookingNotFoundError,
    QuotaExceededError,
    CircuitBreakerOpenError,
    DomainError
)
from src.dto.booking_dto import (
    BookingCreateDTO,
    BookingResponseDTO,
    BookingUpdateDTO,
    QuotaResponseDTO
)
from uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.circuit_breaker import CircuitBreakerRegistry, CircuitBreakerState


class BookingService:
    """Сервис для управления бронированиями с Circuit Breaker"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        pricing_service: PricingService,
        breaker_registry: CircuitBreakerRegistry = None,
        daily_limit: int = 3
    ):
        self.uow = uow
        self.pricing_service = pricing_service
        self.booking_repo = uow.bookings
        self.room_repo = uow.rooms
        self.quota_repo = uow.quotas
        self.breaker_registry = breaker_registry or CircuitBreakerRegistry()
        self.daily_limit = daily_limit
    
    def _get_breaker(self, guest_email: str):
        """Получить Circuit Breaker для пользователя"""
        return self.breaker_registry.get_breaker(guest_email)
    
    def _check_quota(self, guest_email: str, booking_date: date) -> tuple:
        """
        Проверить квоту пользователя на дату.
        Возвращает (может_бронировать, количество_сегодня, осталось)
        """
        quota = self.quota_repo.get_by_email_and_date(guest_email, booking_date)
        today_count = quota.count if quota else 0
        remaining = self.daily_limit - today_count
        return remaining > 0, today_count, remaining
    
    def _check_daily_quota_with_breaker(self, guest_email: str, booking_date: date) -> bool:
        """
        Проверить квоту с использованием Circuit Breaker.
        Если лимит превышен, Circuit Breaker открывается.
        """
        breaker = self._get_breaker(guest_email)
        
        if not breaker.can_execute():
            raise CircuitBreakerOpenError(
                f"Circuit Breaker открыт для пользователя {guest_email}. "
                f"Попробуйте позже.",
                details=breaker.get_state_info()
            )
        
        can_book, today_count, remaining = self._check_quota(guest_email, booking_date)
        
        if not can_book:
            breaker.record_failure(
                QuotaExceededError(
                    f"Превышен лимит бронирований для {guest_email}"
                )
            )
            raise QuotaExceededError(
                f"Превышен лимит бронирований для {guest_email}. "
                f"Сегодня: {today_count}, максимум: {self.daily_limit}. "
                f"Осталось попыток: {breaker.max_attempts - breaker.failure_count}",
                details={
                    'today_count': today_count,
                    'daily_limit': self.daily_limit,
                    'remaining': remaining,
                    'breaker_state': breaker.state.value,
                    'failure_count': breaker.failure_count
                }
            )
        
        breaker.record_success()
        return True
    
    def get_quota_status(self, guest_email: str) -> QuotaResponseDTO:
        """Получить статус квоты для пользователя"""
        today = date.today()
        quota = self.quota_repo.get_by_email_and_date(guest_email, today)
        today_count = quota.count if quota else 0
        remaining = self.daily_limit - today_count
        breaker = self._get_breaker(guest_email)
        
        return QuotaResponseDTO(
            guest_email=guest_email,
            today_bookings=today_count,
            max_limit=self.daily_limit,
            remaining=max(0, remaining),
            can_book=remaining > 0 and breaker.can_execute(),
            circuit_breaker_state=breaker.state.value
        )
    
    def create(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        """Создать новое бронирование с проверкой квоты"""
        
        # 1. Проверяем квоту с Circuit Breaker
        self._check_daily_quota_with_breaker(dto.guest_email, dto.check_in)
        
        # 2. Проверяем существование номера
        room = self.room_repo.get_by_id(dto.room_id)
        if not room:
            raise RoomNotFoundError(f"Номер {dto.room_id} не найден")
        if not room.is_active:
            raise RoomNotFoundError(f"Номер {dto.room_id} не активен")
        
        # 3. Проверяем пересечения бронирований
        existing = self.booking_repo.get_by_room_and_dates(
            dto.room_id, dto.check_in, dto.check_out
        )
        if existing:
            raise BookingConflictError(
                f"Номер {dto.room_id} уже забронирован на эти даты",
                details={"conflicting_bookings": [b.id for b in existing]}
            )
        
        # 4. Рассчитываем стоимость
        total_price = self.pricing_service.calculate_price(
            room, dto.check_in, dto.check_out
        )
        
        # 5. Создаем бронирование
        booking = Booking(
            id=None,
            room_id=dto.room_id,
            guest_name=dto.guest_name,
            guest_email=dto.guest_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_price=total_price,
            status=BookingStatus.PENDING
        )
        
        # 6. Сохраняем бронирование
        saved = self.booking_repo.add(booking)
        
        # 7. Увеличиваем счетчик квоты
        self.quota_repo.increment_booking_count(dto.guest_email, dto.check_in)
        
        self.uow.commit()
        
        return BookingResponseDTO(
            id=saved.id,
            room_id=saved.room_id,
            guest_name=saved.guest_name,
            guest_email=saved.guest_email,
            check_in=saved.check_in,
            check_out=saved.check_out,
            total_price=saved.total_price,
            status=saved.status.value,
            created_at=saved.created_at
        )
    
    def cancel(self, booking_id: int) -> bool:
        """Отменить бронирование и уменьшить счетчик квоты"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")
        
        if booking.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise DomainError(
                f"Нельзя отменить бронирование в статусе {booking.status.value}"
            )
        
        # Меняем статус
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        self.booking_repo.update(booking)
        
        # Уменьшаем счетчик квоты (для сегодняшней даты)
        today = date.today()
        self.quota_repo.decrement_booking_count(booking.guest_email, today)
        
        # Сбрасываем Circuit Breaker при успешной отмене
        breaker = self._get_breaker(booking.guest_email)
        breaker.record_success()
        
        self.uow.commit()
        return True
    
    def get_available_rooms(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        capacity: Optional[int] = None
    ) -> List[dict]:
        """Получить доступные номера в отеле на указанные даты"""
        rooms = self.room_repo.get_by_hotel(hotel_id, active_only=True)
        
        if capacity:
            rooms = [r for r in rooms if r.capacity >= capacity]
        
        available = []
        for room in rooms:
            existing = self.booking_repo.get_by_room_and_dates(
                room.id, check_in, check_out
            )
            if not existing:
                available.append({
                    'room_id': room.id,
                    'number': room.number,
                    'capacity': room.capacity,
                    'price_per_night': room.price_per_night
                })
        
        return available
    
    def confirm(self, booking_id: int) -> None:
        """Подтвердить бронирование (администратор)"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")
        
        if booking.status != BookingStatus.PENDING:
            raise DomainError(
                f"Бронирование в статусе {booking.status.value} нельзя подтвердить"
            )
        
        booking.status = BookingStatus.CONFIRMED
        self.booking_repo.update(booking)
        self.uow.commit()
    
    def reset_breaker(self, guest_email: str) -> None:
        """Сбросить Circuit Breaker для пользователя (администратор)"""
        self.breaker_registry.reset_breaker(guest_email)
    
    def get_breaker_status(self, guest_email: str) -> dict:
        """Получить статус Circuit Breaker для пользователя"""
        breaker = self._get_breaker(guest_email)
        return breaker.get_state_info()
    
    def get_all_breaker_statuses(self) -> dict:
        """Получить статусы всех Circuit Breaker"""
        return self.breaker_registry.get_all_states()