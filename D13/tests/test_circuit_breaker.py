# tests/test_circuit_breaker.py
import pytest
from datetime import datetime, timedelta
from src.services.circuit_breaker import BookingCircuitBreaker, CircuitBreakerRegistry
from src.domain.models import CircuitBreakerState


class TestCircuitBreaker:
    """Тесты для Circuit Breaker"""
    
    def test_initial_state_closed(self):
        """Тест: начальное состояние CLOSED"""
        breaker = BookingCircuitBreaker("test@example.com")
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.can_execute() is True
    
    def test_failure_count_increments(self):
        """Тест: увеличение счетчика неудач"""
        breaker = BookingCircuitBreaker("test@example.com", failure_threshold=3)
        
        breaker.record_failure()
        assert breaker.failure_count == 1
        assert breaker.can_execute() is True
        
        breaker.record_failure()
        assert breaker.failure_count == 2
        assert breaker.can_execute() is True
        
        breaker.record_failure()
        assert breaker.failure_count == 3
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.can_execute() is False
    
    def test_circuit_breaker_opens_on_threshold(self):
        """Тест: Circuit Breaker открывается при достижении порога"""
        breaker = BookingCircuitBreaker("test@example.com", failure_threshold=2)
        
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.CLOSED
        
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
    
    def test_circuit_breaker_transitions_to_half_open(self):
        """Тест: переход из OPEN в HALF_OPEN после таймаута"""
        breaker = BookingCircuitBreaker(
            "test@example.com",
            failure_threshold=2,
            timeout_seconds=10
        )
        
        # Открываем Circuit Breaker
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Имитируем прохождение времени
        breaker.next_attempt_time = datetime.now() - timedelta(seconds=1)
        
        # Проверяем переход в HALF_OPEN
        assert breaker.can_execute() is True
        assert breaker.state == CircuitBreakerState.HALF_OPEN
    
    def test_success_closes_circuit_breaker(self):
        """Тест: успешное выполнение закрывает Circuit Breaker"""
        breaker = BookingCircuitBreaker("test@example.com", failure_threshold=2)
        
        # Открываем Circuit Breaker
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Имитируем прохождение времени
        breaker.next_attempt_time = datetime.now() - timedelta(seconds=1)
        breaker.can_execute()  # Переход в HALF_OPEN
        
        # Записываем успех
        breaker.record_success()
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
    
    def test_failure_in_half_open_opens_again(self):
        """Тест: неудача в HALF_OPEN снова открывает Circuit Breaker"""
        breaker = BookingCircuitBreaker("test@example.com", failure_threshold=2)
        
        # Открываем Circuit Breaker
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Переходим в HALF_OPEN
        breaker.next_attempt_time = datetime.now() - timedelta(seconds=1)
        breaker.can_execute()
        assert breaker.state == CircuitBreakerState.HALF_OPEN
        
        # Неудача в HALF_OPEN
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
    
    def test_get_state_info(self):
        """Тест: получение информации о состоянии"""
        breaker = BookingCircuitBreaker("test@example.com")
        info = breaker.get_state_info()
        
        assert info['email'] == "test@example.com"
        assert info['state'] == "closed"
        assert info['failure_count'] == 0
        assert info['failure_threshold'] == 3


class TestCircuitBreakerRegistry:
    """Тесты для CircuitBreakerRegistry"""
    
    def test_get_breaker_creates_new(self):
        """Тест: создание нового Circuit Breaker для нового пользователя"""
        registry = CircuitBreakerRegistry()
        breaker = registry.get_breaker("new@example.com")
        
        assert breaker is not None
        assert breaker.guest_email == "new@example.com"
    
    def test_get_breaker_returns_existing(self):
        """Тест: возврат существующего Circuit Breaker"""
        registry = CircuitBreakerRegistry()
        breaker1 = registry.get_breaker("test@example.com")
        breaker2 = registry.get_breaker("test@example.com")
        
        assert breaker1 is breaker2
    
    def test_reset_breaker(self):
        """Тест: сброс Circuit Breaker"""
        registry = CircuitBreakerRegistry()
        breaker = registry.get_breaker("test@example.com")
        
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        
        registry.reset_breaker("test@example.com")
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
    
    def test_remove_breaker(self):
        """Тест: удаление Circuit Breaker"""
        registry = CircuitBreakerRegistry()
        registry.get_breaker("test@example.com")
        assert len(registry._breakers) == 1
        
        registry.remove_breaker("test@example.com")
        assert len(registry._breakers) == 0
    
    def test_get_all_states(self):
        """Тест: получение всех состояний"""
        registry = CircuitBreakerRegistry()
        registry.get_breaker("user1@example.com")
        registry.get_breaker("user2@example.com")
        
        states = registry.get_all_states()
        assert len(states) == 2
        assert "user1@example.com" in states
        assert "user2@example.com" in states