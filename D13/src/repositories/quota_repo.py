# src/repositories/quota_repo.py
from typing import Optional, List
from datetime import date, datetime
from src.domain.models import DailyBookingQuota
from src.repositories.base import BaseRepository


class QuotaRepository(BaseRepository[DailyBookingQuota]):
    """Репозиторий для управления квотами пользователей"""
    
    def __init__(self):
        self._storage: dict[str, DailyBookingQuota] = {}  # key: email_date
        self._next_id = 1
    
    def _make_key(self, guest_email: str, booking_date: date) -> str:
        """Создать ключ для хранилища"""
        return f"{guest_email}_{booking_date}"
    
    def get_by_email_and_date(
        self, 
        guest_email: str, 
        booking_date: date
    ) -> Optional[DailyBookingQuota]:
        """Получить квоту пользователя на конкретную дату"""
        key = self._make_key(guest_email, booking_date)
        return self._storage.get(key)
    
    def get_all_by_email(self, guest_email: str) -> List[DailyBookingQuota]:
        """Получить все квоты пользователя"""
        return [
            quota for quota in self._storage.values()
            if quota.guest_email == guest_email
        ]
    
    def get_today_quota(self, guest_email: str) -> Optional[DailyBookingQuota]:
        """Получить квоту пользователя на сегодня"""
        today = date.today()
        return self.get_by_email_and_date(guest_email, today)
    
    def increment_booking_count(
        self, 
        guest_email: str, 
        booking_date: date
    ) -> DailyBookingQuota:
        """Увеличить счетчик бронирований"""
        quota = self.get_by_email_and_date(guest_email, booking_date)
        
        if quota is None:
            # Создаем новую запись о квоте
            quota = DailyBookingQuota(
                id=self._next_id,
                guest_email=guest_email,
                booking_date=booking_date,
                count=1,
                limit=3,
                last_updated=datetime.now()
            )
            self._storage[self._make_key(guest_email, booking_date)] = quota
            self._next_id += 1
        else:
            quota.count += 1
            quota.last_updated = datetime.now()
            self._storage[self._make_key(guest_email, booking_date)] = quota
        
        return quota
    
    def decrement_booking_count(
        self, 
        guest_email: str, 
        booking_date: date
    ) -> Optional[DailyBookingQuota]:
        """Уменьшить счетчик бронирований"""
        quota = self.get_by_email_and_date(guest_email, booking_date)
        
        if quota and quota.count > 0:
            quota.count -= 1
            quota.last_updated = datetime.now()
            self._storage[self._make_key(guest_email, booking_date)] = quota
            return quota
        
        return None
    
    def reset_quota(self, guest_email: str, booking_date: date) -> bool:
        """Сбросить квоту на конкретную дату"""
        key = self._make_key(guest_email, booking_date)
        if key in self._storage:
            del self._storage[key]
            return True
        return False
    
    def get_by_id(self, id: int) -> Optional[DailyBookingQuota]:
        """Получить квоту по ID"""
        for quota in self._storage.values():
            if quota.id == id:
                return quota
        return None
    
    def get_all(self, **filters) -> List[DailyBookingQuota]:
        """Получить все квоты с фильтрацией"""
        result = list(self._storage.values())
        if 'guest_email' in filters:
            result = [q for q in result if q.guest_email == filters['guest_email']]
        if 'booking_date' in filters:
            result = [q for q in result if q.booking_date == filters['booking_date']]
        return result
    
    def update(self, entity: DailyBookingQuota) -> DailyBookingQuota:
        """Обновить квоту"""
        key = self._make_key(entity.guest_email, entity.booking_date)
        if key not in self._storage:
            raise ValueError(f"Quota for {entity.guest_email} on {entity.booking_date} not found")
        self._storage[key] = entity
        return entity
    
    def delete(self, id: int) -> bool:
        """Удалить квоту по ID"""
        for key, quota in list(self._storage.items()):
            if quota.id == id:
                del self._storage[key]
                return True
        return False