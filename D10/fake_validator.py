"""
Фальшивая эталонная реализация валидатора заказов.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
from pydantic import BaseModel, Field, ValidationError, validator


class OrderItem(BaseModel):
    """Модель позиции заказа"""
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=1, le=999)
    price: float = Field(..., ge=0.01, le=1000000)


class Order(BaseModel):
    """Модель заказа"""
    order_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    items: List[OrderItem] = Field(..., min_items=1, max_items=100)
    total_amount: float = Field(..., ge=0.01, le=10000000)
    order_time: datetime
    user_created_at: datetime

    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        """Проверяем соответствие суммы сумме позиций"""
        if 'items' in values:
            calculated = sum(item.price * item.quantity for item in values['items'])
            if abs(v - calculated) > 0.01:
                raise ValueError(f"Total amount {v} does not match sum of items {calculated}")
        return v


class FakeValidator:
    """Фальшивый валидатор для тестирования."""
    
    def __init__(self, chaos_mode: bool = False, chaos_probability: float = 0.05):
        self.chaos_mode = chaos_mode
        self.chaos_probability = chaos_probability
        
        self.MAX_TOTAL_AMOUNT = 100000
        self.MAX_ITEMS_COUNT = 100
        self.MIN_ITEMS_COUNT = 1
        self.MAX_ITEM_QUANTITY = 100
        self.WORK_START_HOUR = 8
        self.WORK_END_HOUR = 23
        self.WORK_START_MINUTE = 0
        self.WORK_END_MINUTE = 0
        self.MIN_USER_AGE_DAYS = 1
        self.HIGH_AMOUNT_THRESHOLD = 50000
        self.HIGH_ITEMS_THRESHOLD = 20
        self.NEW_USER_DAYS = 7
        
    def validate_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод валидации заказа."""
        
        # Хаос-режим
        if self.chaos_mode and random.random() < self.chaos_probability:
            return self._chaos_response()
        
        try:
            order = Order(**order_data)
        except ValidationError as e:
            return {
                "valid": False,
                "risk_score": 0.0,
                "reasons": [f"Ошибка формата данных: {str(e)}"]
            }
        
        reasons = []
        is_valid = True
        
        # Правило 1: Проверка суммы
        if order.total_amount > self.MAX_TOTAL_AMOUNT:
            is_valid = False
            reasons.append(f"Сумма заказа превышает допустимый лимит (макс. {self.MAX_TOTAL_AMOUNT})")
        
        # Правило 2: Проверка количества позиций
        if not (self.MIN_ITEMS_COUNT <= len(order.items) <= self.MAX_ITEMS_COUNT):
            is_valid = False
            reasons.append(f"Некорректное количество позиций в заказе (мин. {self.MIN_ITEMS_COUNT}, макс. {self.MAX_ITEMS_COUNT})")
        
        # Правило 3: Проверка времени работы (с учетом минут)
        order_hour = order.order_time.hour
        order_minute = order.order_time.minute
        order_second = order.order_time.second
        
        # Проверяем, что время в диапазоне [08:00:00, 23:00:00]
        is_work_time = False
        if self.WORK_START_HOUR < order_hour < self.WORK_END_HOUR:
            is_work_time = True
        elif order_hour == self.WORK_START_HOUR and order_minute >= self.WORK_START_MINUTE:
            is_work_time = True
        elif order_hour == self.WORK_END_HOUR and order_minute == self.WORK_END_MINUTE and order_second == 0:
            is_work_time = True
        
        if not is_work_time:
            is_valid = False
            reasons.append(f"Заказы принимаются только с {self.WORK_START_HOUR}:00 до {self.WORK_END_HOUR}:00 UTC")
        
        # Правило 4: Проверка возраста пользователя
        user_age = order.order_time - order.user_created_at
        if user_age < timedelta(days=self.MIN_USER_AGE_DAYS):
            is_valid = False
            reasons.append(f"Пользователь должен быть зарегистрирован минимум {self.MIN_USER_AGE_DAYS} день")
        
        # Правило 5: Проверка количества одинаковых товаров
        for item in order.items:
            if item.quantity > self.MAX_ITEM_QUANTITY:
                is_valid = False
                reasons.append(f"Превышено максимальное количество одного товара (макс. {self.MAX_ITEM_QUANTITY})")
                break
        
        # Расчет risk_score (только для валидных заказов)
        risk_score = 0.0
        if is_valid:
            risk_factors = []
            
            # Фактор 1: Высокая сумма
            if order.total_amount > self.HIGH_AMOUNT_THRESHOLD:
                risk_score += 0.3
                risk_factors.append("high_amount")
            
            # Фактор 2: Много позиций
            if len(order.items) > self.HIGH_ITEMS_THRESHOLD:
                risk_score += 0.2
                risk_factors.append("many_items")
            
            # Фактор 3: Позднее время (22:00-23:00)
            if order_hour >= 22:
                risk_score += 0.2
                risk_factors.append("late_time")
            
            # Фактор 4: Новый пользователь
            if user_age < timedelta(days=self.NEW_USER_DAYS):
                risk_score += 0.3
                risk_factors.append("new_user")
            
            # Фактор 5: Повторяющиеся товары
            product_ids = [item.product_id for item in order.items]
            if len(product_ids) != len(set(product_ids)):
                risk_score += 0.1
                risk_factors.append("duplicate_products")
            
            risk_score = min(1.0, risk_score)
            
            if risk_score >= 0.7:
                reasons.append(f"Высокий уровень риска: {', '.join(risk_factors)}")
        
        return {
            "valid": is_valid,
            "risk_score": risk_score,
            "reasons": reasons
        }
    
    def _chaos_response(self) -> Dict[str, Any]:
        chaos_type = random.choice(['invalid', 'wrong_risk', 'extra_reason', 'empty'])
        
        if chaos_type == 'invalid':
            return {
                "valid": False,
                "risk_score": random.random(),
                "reasons": ["CHAOS: Непредсказуемая ошибка валидации"]
            }
        elif chaos_type == 'wrong_risk':
            return {
                "valid": True,
                "risk_score": random.uniform(-0.5, 1.5),
                "reasons": ["CHAOS: Некорректный риск-скор"]
            }
        elif chaos_type == 'extra_reason':
            return {
                "valid": True,
                "risk_score": 0.5,
                "reasons": ["CHAOS: Лишнее сообщение"]
            }
        else:
            return {
                "valid": True,
                "risk_score": 0.0,
                "reasons": []
            }


def create_validator(chaos_mode: bool = False) -> FakeValidator:
    return FakeValidator(chaos_mode=chaos_mode)