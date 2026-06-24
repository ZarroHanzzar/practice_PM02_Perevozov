
# src/services/circuit_breaker.py
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from src.domain.models import CircuitBreakerState
from src.domain.exceptions import CircuitBreakerOpenError


class BookingCircuitBreaker:
    """
    Circuit Breaker для управления квотами на бронирования.
    Блокирует создание новых бронирований при превышении лимита.
    """
    
    def __init__(
        self,
        guest_email: str,
        max_attempts: int = 3,
        timeout_seconds: int = 60,
        failure_threshold: int = 3
    ):
        self.guest_email = guest_email
        self.max_attempts = max_attempts
        self.timeout_seconds = timeout_seconds
        self.failure_threshold = failure_threshold
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self.next_attempt_time: Optional[datetime] = None
        self.failures: List[Dict] = []
    
    def can_execute(self) -> bool:
        """Проверить, можно ли выполнить операцию"""
        current_time = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
            
        elif self.state == CircuitBreakerState.OPEN:
            if self.next_attempt_time and current_time >= self.next_attempt_time:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
            
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Записать успешное выполнение"""
        self.failure_count = 0
        self.last_success_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.next_attempt_time = None
    
    def record_failure(self, error: Exception = None):
        """Записать неудачное выполнение"""
        current_time = datetime.now()
        self.last_failure_time = current_time
        self.failure_count += 1
        self.failures.append({
            'timestamp': current_time.isoformat(),
            'error': str(error) if error else 'Unknown error'
        })
        
        if len(self.failures) > 10:
            self.failures = self.failures[-10:]
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self.next_attempt_time = current_time + timedelta(seconds=self.timeout_seconds)
                
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.next_attempt_time = current_time + timedelta(seconds=self.timeout_seconds)
    
    def get_state_info(self) -> dict:
        """Получить информацию о состоянии Circuit Breaker"""
        return {
            'email': self.guest_email,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success': self.last_success_time.isoformat() if self.last_success_time else None,
            'next_attempt': self.next_attempt_time.isoformat() if self.next_attempt_time else None,
            'recent_failures': len(self.failures)
        }
    
    def reset(self):
        """Сбросить состояние Circuit Breaker"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.next_attempt_time = None
        self.failures = []


class CircuitBreakerRegistry:
    """Реестр Circuit Breaker для разных пользователей"""
    
    def __init__(self):
        self._breakers: Dict[str, BookingCircuitBreaker] = {}
    
    def get_breaker(self, guest_email: str) -> BookingCircuitBreaker:
        """Получить Circuit Breaker для пользователя"""
        if guest_email not in self._breakers:
            self._breakers[guest_email] = BookingCircuitBreaker(
                guest_email=guest_email,
                max_attempts=3,
                timeout_seconds=60,
                failure_threshold=3
            )
        return self._breakers[guest_email]
    
    def reset_breaker(self, guest_email: str):
        """Сбросить Circuit Breaker для пользователя"""
        if guest_email in self._breakers:
            self._breakers[guest_email].reset()
    
    def remove_breaker(self, guest_email: str):
        """Удалить Circuit Breaker для пользователя"""
        if guest_email in self._breakers:
            del self._breakers[guest_email]
    
    def get_all_states(self) -> Dict[str, dict]:
        """Получить состояния всех Circuit Breaker"""
        return {
            email: breaker.get_state_info()
            for email, breaker in self._breakers.items()
        }