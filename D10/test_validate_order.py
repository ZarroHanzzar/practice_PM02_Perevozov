"""
Параметризованные тесты для валидатора заказов.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
import random

from fake_validator import create_validator


# ============= ФИКСТУРЫ =============

@pytest.fixture
def validator():
    return create_validator(chaos_mode=False)


@pytest.fixture
def chaos_validator():
    return create_validator(chaos_mode=True)


# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

def create_order(
    total_amount: float = 100.0,
    items_count: int = 1,
    order_hour: int = 10,
    user_age_days: int = 10,
    duplicate_products: bool = False,
    item_quantity: int = 1,
    minutes: int = 0,
    seconds: int = 0
) -> Dict[str, Any]:
    """Создает тестовый заказ с заданными параметрами"""
    
    # Создаем время с указанными hour, minutes, seconds
    now = datetime(2026, 6, 16, order_hour, minutes, seconds)
    user_created = now - timedelta(days=user_age_days)
    
    items = []
    if items_count > 0 and item_quantity > 0:
        price_per_item = total_amount / (items_count * item_quantity)
        price_per_item = round(max(0.01, price_per_item), 2)
    else:
        price_per_item = 10.0
    
    for i in range(items_count):
        product_id = f"PRD-{i:03d}"
        if duplicate_products and i >= 2:
            product_id = "PRD-000"
        items.append({
            "product_id": product_id,
            "quantity": item_quantity,
            "price": price_per_item
        })
    
    calculated_total = sum(item["price"] * item["quantity"] for item in items)
    
    return {
        "order_id": f"ORD-{datetime.now().timestamp()}",
        "user_id": f"USR-{datetime.now().timestamp()}",
        "items": items,
        "total_amount": round(calculated_total, 2),
        "order_time": now.isoformat(),
        "user_created_at": user_created.isoformat()
    }


# ============= ПАРАМЕТРИЗОВАННЫЕ ТЕСТЫ =============

@pytest.mark.parametrize("test_data", [
    # TC-001: Минимальная сумма
    {
        "total_amount": 0.01,
        "items_count": 1,
        "order_hour": 10,
        "user_age_days": 10,
        "expected_valid": True,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
    # TC-002: Высокая сумма (риск)
    {
        "total_amount": 60000,
        "items_count": 1,
        "order_hour": 10,
        "user_age_days": 10,
        "expected_valid": True,
        "expected_risk_min": 0.3,
        "expected_risk_max": 0.3,
    },
    # TC-003: Сумма > лимита
    {
        "total_amount": 100000.01,
        "items_count": 1,
        "order_hour": 10,
        "user_age_days": 10,
        "expected_valid": False,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
    # TC-004: Много позиций (риск)
    {
        "total_amount": 1000,
        "items_count": 25,
        "order_hour": 10,
        "user_age_days": 10,
        "expected_valid": True,
        "expected_risk_min": 0.2,
        "expected_risk_max": 0.2,
    },
    # TC-005: Кол-во позиций > 100
    {
        "total_amount": 1000,
        "items_count": 150,
        "order_hour": 10,
        "user_age_days": 10,
        "expected_valid": False,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
    # TC-006: Время 08:00 (граница)
    {
        "total_amount": 100,
        "items_count": 1,
        "order_hour": 8,
        "user_age_days": 10,
        "expected_valid": True,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
    # TC-007: Время 23:00 (граница)
    {
        "total_amount": 100,
        "items_count": 1,
        "order_hour": 23,
        "user_age_days": 10,
        "expected_valid": True,
        "expected_risk_min": 0.2,
        "expected_risk_max": 0.2,
    },
    # TC-008: Время 07:59 - НЕВАЛИДНО
    {
        "total_amount": 100,
        "items_count": 1,
        "order_hour": 7,
        "minutes": 59,
        "user_age_days": 10,
        "expected_valid": False,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
    # TC-009: Время 23:01 - НЕВАЛИДНО
    {
        "total_amount": 100,
        "items_count": 1,
        "order_hour": 23,
        "minutes": 1,
        "user_age_days": 10,
        "expected_valid": False,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
    # TC-010: Новый пользователь (риск)
    {
        "total_amount": 100,
        "items_count": 1,
        "order_hour": 10,
        "user_age_days": 2,
        "expected_valid": True,
        "expected_risk_min": 0.3,
        "expected_risk_max": 0.3,
    },
    # TC-011: Возраст < 1 день - НЕВАЛИДНО
    {
        "total_amount": 100,
        "items_count": 1,
        "order_hour": 10,
        "user_age_days": 0,
        "expected_valid": False,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
    # TC-012: Высокая сумма + много позиций
    {
        "total_amount": 60000,
        "items_count": 25,
        "order_hour": 10,
        "user_age_days": 10,
        "expected_valid": True,
        "expected_risk_min": 0.5,
        "expected_risk_max": 0.5,
    },
    # TC-013: Позднее время + новый пользователь
    {
        "total_amount": 100,
        "items_count": 1,
        "order_hour": 22,
        "minutes": 30,
        "user_age_days": 2,
        "expected_valid": True,
        "expected_risk_min": 0.5,
        "expected_risk_max": 0.5,
    },
    # TC-014: Все факторы риска
    {
        "total_amount": 70000,
        "items_count": 30,
        "order_hour": 22,
        "minutes": 30,
        "user_age_days": 2,
        "duplicate_products": True,
        "expected_valid": True,
        "expected_risk_min": 1.0,
        "expected_risk_max": 1.0,
    },
    # TC-015: Дубликаты товаров
    {
        "total_amount": 1000,
        "items_count": 3,
        "order_hour": 10,
        "user_age_days": 10,
        "duplicate_products": True,
        "expected_valid": True,
        "expected_risk_min": 0.1,
        "expected_risk_max": 0.1,
    },
    # TC-016: Невалидная сумма + невалидное время
    {
        "total_amount": 150000,
        "items_count": 1,
        "order_hour": 2,
        "user_age_days": 10,
        "expected_valid": False,
        "expected_risk_min": 0.0,
        "expected_risk_max": 0.0,
    },
])
def test_validate_order_decision_table(validator, test_data):
    """Тестирование всех комбинаций из decision table"""
    
    order = create_order(
        total_amount=test_data["total_amount"],
        items_count=test_data["items_count"],
        order_hour=test_data["order_hour"],
        user_age_days=test_data.get("user_age_days", 10),
        duplicate_products=test_data.get("duplicate_products", False),
        minutes=test_data.get("minutes", 0)
    )
    
    result = validator.validate_order(order)
    
    assert result["valid"] == test_data["expected_valid"], \
        f"Order: {order}\nExpected valid={test_data['expected_valid']}, got {result['valid']}. Reasons: {result['reasons']}"
    
    if test_data["expected_valid"]:
        assert test_data["expected_risk_min"] <= result["risk_score"] <= test_data["expected_risk_max"], \
            f"Risk score {result['risk_score']} outside range [{test_data['expected_risk_min']}, {test_data['expected_risk_max']}]"


# ============= ТЕСТЫ НА ВРЕМЕННЫЕ ГРАНИЦЫ =============

def test_time_boundary_07_59_59(validator):
    """07:59:59 - невалидно"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=7,
        minutes=59,
        seconds=59,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    assert result["valid"] is False
    found = any("только с 8:00" in r for r in result["reasons"])
    assert found, f"Expected time error at 07:59:59, got {result['reasons']}"


def test_time_boundary_08_00_00(validator):
    """08:00:00 - валидно (по времени)"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=8,
        minutes=0,
        seconds=0,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    time_reason = any("только с 8:00" in r for r in result["reasons"])
    assert not time_reason, f"Unexpected time error at 08:00:00: {result['reasons']}"


def test_time_boundary_22_59_59(validator):
    """22:59:59 - валидно (по времени)"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=22,
        minutes=59,
        seconds=59,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    time_reason = any("только с 8:00" in r for r in result["reasons"])
    assert not time_reason, f"Unexpected time error at 22:59:59: {result['reasons']}"


def test_time_boundary_23_00_00(validator):
    """23:00:00 - валидно (граница)"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=23,
        minutes=0,
        seconds=0,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    time_reason = any("только с 8:00" in r for r in result["reasons"])
    assert not time_reason, f"Unexpected time error at 23:00:00: {result['reasons']}"


def test_time_boundary_23_00_01(validator):
    """23:00:01 - невалидно"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=23,
        minutes=0,
        seconds=1,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    assert result["valid"] is False, f"Expected invalid at 23:00:01, got valid. Reasons: {result['reasons']}"
    found = any("только с 8:00" in r for r in result["reasons"])
    assert found, f"Expected time error at 23:00:01, got {result['reasons']}"


# ============= ТЕСТЫ НА ИНВАРИАНТЫ =============

def test_risk_score_always_in_range(validator):
    """Проверка, что risk_score всегда в диапазоне [0, 1]"""
    for _ in range(50):
        order = create_order(
            total_amount=random.uniform(0.01, 150000),
            items_count=random.randint(1, 50),
            order_hour=random.randint(0, 23),
            user_age_days=random.randint(0, 30)
        )
        result = validator.validate_order(order)
        assert 0 <= result["risk_score"] <= 1, \
            f"Risk score {result['risk_score']} outside [0, 1]"


def test_invalid_order_has_reason(validator):
    """Проверка: если valid=False, то есть причина"""
    invalid_count = 0
    for _ in range(50):
        order = create_order(
            total_amount=random.uniform(100000.01, 200000),
            items_count=random.randint(1, 10),
            order_hour=random.randint(0, 7),
            user_age_days=random.randint(0, 0)
        )
        result = validator.validate_order(order)
        if result["valid"] is False:
            invalid_count += 1
            assert len(result["reasons"]) > 0, "Invalid order has no reasons"
    assert invalid_count > 0, "No invalid orders generated"


def test_valid_order_risk_score_consistent(validator):
    """Проверка, что риск-скор считается консистентно"""
    # Заказ с низким риском
    order_low = create_order(
        total_amount=100,
        items_count=1,
        order_hour=10,
        user_age_days=10
    )
    result_low = validator.validate_order(order_low)
    assert result_low["valid"] is True
    assert result_low["risk_score"] == 0.0
    
    # Заказ с высоким риском
    order_high = create_order(
        total_amount=70000,
        items_count=30,
        order_hour=22,
        minutes=30,
        user_age_days=2,
        duplicate_products=True
    )
    result_high = validator.validate_order(order_high)
    assert result_high["valid"] is True
    assert result_high["risk_score"] == 1.0


# ============= ТЕСТЫ НА УСТОЙЧИВОСТЬ =============

def test_duplicate_orders_stability(validator):
    """Проверка устойчивости к дубликатам заказов"""
    order_data = create_order(
        total_amount=100,
        items_count=1,
        order_hour=10,
        user_age_days=10
    )
    
    results = []
    for _ in range(10):
        result = validator.validate_order(order_data)
        results.append(result)
        assert isinstance(result["valid"], bool)
        assert 0 <= result["risk_score"] <= 1
        assert isinstance(result["reasons"], list)
    
    # Все результаты должны быть одинаковыми
    for i in range(1, len(results)):
        assert results[i]["valid"] == results[0]["valid"]
        assert results[i]["risk_score"] == results[0]["risk_score"]
        assert results[i]["reasons"] == results[0]["reasons"]


def test_many_random_orders(validator):
    """Запуск 50 случайных заказов и проверка инвариантов"""
    for _ in range(50):
        order = create_order(
            total_amount=random.uniform(0.01, 200000),
            items_count=random.randint(1, 50),
            order_hour=random.randint(0, 23),
            user_age_days=random.randint(0, 30),
            duplicate_products=random.choice([True, False]),
            item_quantity=random.randint(1, 50)
        )
        
        result = validator.validate_order(order)
        
        # Инварианты
        assert isinstance(result["valid"], bool), "valid must be bool"
        assert 0 <= result["risk_score"] <= 1, "risk_score must be in [0, 1]"
        assert isinstance(result["reasons"], list), "reasons must be list"
        
        # Если невалиден - есть причина
        if result["valid"] is False:
            assert len(result["reasons"]) > 0, "Invalid order must have reasons"


def test_chaos_mode(chaos_validator):
    """Проверка устойчивости тестов к хаос-режиму"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=10,
        user_age_days=10
    )
    
    for _ in range(30):
        try:
            result = chaos_validator.validate_order(order)
            assert isinstance(result["valid"], bool)
            assert isinstance(result["reasons"], list)
        except Exception as e:
            pytest.fail(f"Validator crashed: {e}")


# ============= ТЕСТЫ НА СПЕЦИФИЧНЫЕ СЦЕНАРИИ =============

def test_order_just_before_midnight(validator):
    """Заказ в 23:00:00 - должен быть валидным"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=23,
        minutes=0,
        seconds=0,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    assert result["valid"] is True
    assert result["risk_score"] == 0.2  # Позднее время


def test_order_just_after_midnight(validator):
    """Заказ в 23:00:01 - должен быть невалидным"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=23,
        minutes=0,
        seconds=1,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    assert result["valid"] is False
    found = any("только с 8:00" in r for r in result["reasons"])
    assert found, f"Expected time error, got {result['reasons']}"


def test_order_very_high_amount(validator):
    """Заказ с очень высокой суммой - невалиден"""
    order = create_order(
        total_amount=1000000,
        items_count=1,
        order_hour=10,
        user_age_days=10
    )
    
    result = validator.validate_order(order)
    assert result["valid"] is False
    found = any("превышает допустимый лимит" in r for r in result["reasons"])
    assert found, f"Expected amount error, got {result['reasons']}"


def test_order_new_user(validator):
    """Заказ от нового пользователя - валиден, но с высоким риском"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=10,
        user_age_days=1  # 1 день - минимальный возраст
    )
    
    result = validator.validate_order(order)
    assert result["valid"] is True
    assert result["risk_score"] == 0.3  # Новый пользователь


def test_order_very_new_user(validator):
    """Заказ от очень нового пользователя (< 1 дня) - невалиден"""
    order = create_order(
        total_amount=100,
        items_count=1,
        order_hour=10,
        user_age_days=0  # Меньше 1 дня
    )
    
    result = validator.validate_order(order)
    assert result["valid"] is False
    found = any("зарегистрирован минимум 1 день" in r for r in result["reasons"])
    assert found, f"Expected age error, got {result['reasons']}"