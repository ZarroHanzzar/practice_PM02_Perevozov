# src/services/pricing_service.py
from datetime import date, timedelta  # <-- ДОБАВИТЬ timedelta
from typing import Optional
from src.domain.models import Room
from src.domain.exceptions import InvalidDatesError


class PricingService:
    def __init__(self, seasonal_coefficients: Optional[dict] = None):
        self.seasonal_coefficients = seasonal_coefficients or {
            1: 1.1, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
            6: 1.2, 7: 1.5, 8: 1.5, 9: 1.0, 10: 1.0,
            11: 1.0, 12: 1.3,
        }

    def calculate_price(
        self,
        room: Room,
        check_in: date,
        check_out: date
    ) -> float:
        nights = (check_out - check_in).days
        if nights <= 0:
            raise InvalidDatesError("Количество ночей должно быть больше 0")

        total = 0.0
        current_date = check_in

        # ИСПРАВЛЕНИЕ: перебираем дни, а не месяцы
        for _ in range(nights):
            month = current_date.month
            coefficient = self.seasonal_coefficients.get(month, 1.0)
            total += room.price_per_night * coefficient
            current_date += timedelta(days=1)  # <-- ДОБАВИТЬ ЭТУ СТРОКУ

        if nights >= 14:
            total *= 0.855
        elif nights >= 7:
            total *= 0.95

        return round(total, 2)