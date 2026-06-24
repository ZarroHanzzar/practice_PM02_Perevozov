# tests/test_pricing_service.py
import pytest
from datetime import date
from src.services.pricing_service import PricingService
from src.domain.models import Room
from src.domain.exceptions import InvalidDatesError


class TestPricingService:
    """Тесты для PricingService"""
    
    @pytest.fixture
    def pricing_service(self):
        return PricingService()
    
    @pytest.fixture
    def sample_room(self):
        return Room(
            id=1,
            hotel_id=1,
            number="101",
            capacity=2,
            price_per_night=100.0,
            is_active=True,
            room_type="standard"
        )
    
    def test_calculate_price_basic(self, pricing_service, sample_room):
        """Тест: базовый расчет стоимости (5 ночей, без скидки)"""
        check_in = date(2026, 6, 10)
        check_out = date(2026, 6, 15)  # 5 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 5 ночей * 100 * 1.2 (июньский коэффициент) = 600
        assert price == 600.0
    
    def test_calculate_price_january(self, pricing_service, sample_room):
        """Тест: январь (коэффициент 1.1)"""
        check_in = date(2026, 1, 10)
        check_out = date(2026, 1, 15)  # 5 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 5 ночей * 100 * 1.1 = 550
        assert price == 550.0
    
    def test_calculate_price_july(self, pricing_service, sample_room):
        """Тест: июль (коэффициент 1.5)"""
        check_in = date(2026, 7, 10)
        check_out = date(2026, 7, 15)  # 5 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 5 ночей * 100 * 1.5 = 750
        assert price == 750.0
    
    def test_calculate_price_december(self, pricing_service, sample_room):
        """Тест: декабрь (коэффициент 1.3)"""
        check_in = date(2026, 12, 10)
        check_out = date(2026, 12, 15)  # 5 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 5 ночей * 100 * 1.3 = 650
        assert price == 650.0
    
    def test_calculate_price_with_discount_7_days(self, pricing_service, sample_room):
        """Тест: скидка за 7+ дней"""
        check_in = date(2026, 6, 10)
        check_out = date(2026, 6, 17)  # 7 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 7 ночей * 100 * 1.2 * 0.95 = 798
        assert price == 798.0
    
    def test_calculate_price_with_discount_14_days(self, pricing_service, sample_room):
        """Тест: скидка за 14+ дней"""
        check_in = date(2026, 6, 10)
        check_out = date(2026, 6, 24)  # 14 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 14 ночей * 100 * 1.2 * 0.855 = 1436.4
        assert price == 1436.4
    
    def test_calculate_price_invalid_dates(self, pricing_service, sample_room):
        """Тест: некорректные даты (выезд раньше заезда)"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 10)
        
        with pytest.raises(InvalidDatesError):
            pricing_service.calculate_price(sample_room, check_in, check_out)
    
    def test_calculate_price_different_months(self, pricing_service, sample_room):
        """Тест: расчет с разными месяцами (июнь -> июль) с учетом скидки"""
        check_in = date(2026, 6, 25)
        check_out = date(2026, 7, 5)  # 10 ночей, июнь + июль
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # Считаем точно:
        # Июнь: 25, 26, 27, 28, 29, 30 = 6 ночей в июне
        # Июль: 1, 2, 3, 4 = 4 ночи в июле
        # 6 * 100 * 1.2 + 4 * 100 * 1.5 = 720 + 600 = 1320
        # Скидка 5% за 10 ночей (>= 7): 1320 * 0.95 = 1254
        assert price == 1254.0
    
    def test_calculate_price_cross_year(self, pricing_service, sample_room):
        """Тест: переход через новый год (декабрь -> январь) без скидки"""
        check_in = date(2026, 12, 28)
        check_out = date(2027, 1, 3)  # 6 ночей, декабрь + январь
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # Считаем точно (6 ночей < 7, скидки нет):
        # Декабрь: 28, 29, 30, 31 = 4 ночи в декабре (28->29, 29->30, 30->31, 31->1)
        # Январь: 1, 2 = 2 ночи в январе (1->2, 2->3)
        # 4 * 100 * 1.3 + 2 * 100 * 1.1 = 520 + 220 = 740
        assert price == 740.0
    
    def test_calculate_price_one_night(self, pricing_service, sample_room):
        """Тест: одна ночь (без скидки)"""
        check_in = date(2026, 6, 10)
        check_out = date(2026, 6, 11)  # 1 ночь
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 1 ночь * 100 * 1.2 = 120
        assert price == 120.0
    
    def test_calculate_price_no_seasonal(self, pricing_service, sample_room):
        """Тест: месяц без сезонного коэффициента (апрель)"""
        check_in = date(2026, 4, 10)
        check_out = date(2026, 4, 15)  # 5 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 5 ночей * 100 * 1.0 = 500
        assert price == 500.0
    
    def test_calculate_price_long_stay_mixed_months(self, pricing_service, sample_room):
        """Тест: длительное бронирование с разными месяцами и скидкой 14.5%"""
        check_in = date(2026, 6, 25)
        check_out = date(2026, 7, 9)  # 14 ночей, июнь + июль + скидка
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # Июнь: 25-30 = 6 ночей * 100 * 1.2 = 720
        # Июль: 1-9 = 8 ночей * 100 * 1.5 = 1200
        # Итого: 1920 * 0.855 (скидка 14.5%) = 1641.6
        assert price == 1641.6
    
    def test_calculate_price_no_discount_6_nights(self, pricing_service, sample_room):
        """Тест: 6 ночей - скидка не применяется"""
        check_in = date(2026, 6, 10)
        check_out = date(2026, 6, 16)  # 6 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 6 ночей * 100 * 1.2 = 720 (скидки нет)
        assert price == 720.0
    
    def test_calculate_price_exactly_7_nights(self, pricing_service, sample_room):
        """Тест: ровно 7 ночей - применяется скидка 5%"""
        check_in = date(2026, 6, 10)
        check_out = date(2026, 6, 17)  # 7 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 7 ночей * 100 * 1.2 * 0.95 = 798
        assert price == 798.0
    
    def test_calculate_price_exactly_14_nights(self, pricing_service, sample_room):
        """Тест: ровно 14 ночей - применяется скидка 14.5%"""
        check_in = date(2026, 6, 10)
        check_out = date(2026, 6, 24)  # 14 ночей
        
        price = pricing_service.calculate_price(sample_room, check_in, check_out)
        
        # 14 ночей * 100 * 1.2 * 0.855 = 1436.4
        assert price == 1436.4