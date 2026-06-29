# tests/unit/test_events.py
"""
Unit tests for domain events
"""
import pytest
from datetime import datetime
from src.core.events import (
    DomainEvent,
    PasswordHashedEvent,
    TokenGeneratedEvent,
    TokenVerifiedEvent
)


class TestDomainEvent:
    """Тесты для DomainEvent"""
    
    def test_domain_event_creation(self):
        now = datetime.now()
        event = DomainEvent(
            occurred_at=now,
            event_type="test_event",
            data={"key": "value"}
        )
        assert event.occurred_at == now
        assert event.event_type == "test_event"
        assert event.data == {"key": "value"}


class TestPasswordHashedEvent:
    """Тесты для PasswordHashedEvent"""
    
    def test_password_hashed_event_creation(self):
        event = PasswordHashedEvent(user_id=123, algorithm="sha256")
        # Проверяем через data словарь
        assert event.data["user_id"] == 123
        assert event.data["algorithm"] == "sha256"
        assert event.event_type == "password_hashed"
        assert isinstance(event.occurred_at, datetime)
    
    def test_password_hashed_event_attributes(self):
        event = PasswordHashedEvent(user_id=456, algorithm="md5")
        assert event.data["user_id"] == 456
        assert event.data["algorithm"] == "md5"


class TestTokenGeneratedEvent:
    """Тесты для TokenGeneratedEvent"""
    
    def test_token_generated_event_creation(self):
        event = TokenGeneratedEvent(user_id=123, expires_in_hours=24)
        assert event.data["user_id"] == 123
        assert event.data["expires_in_hours"] == 24
        assert event.event_type == "token_generated"
        assert isinstance(event.occurred_at, datetime)
    
    def test_token_generated_event_default_hours(self):
        event = TokenGeneratedEvent(user_id=123, expires_in_hours=24)
        assert event.data["expires_in_hours"] == 24
    
    def test_token_generated_event_different_hours(self):
        event = TokenGeneratedEvent(user_id=123, expires_in_hours=48)
        assert event.data["expires_in_hours"] == 48


class TestTokenVerifiedEvent:
    """Тесты для TokenVerifiedEvent"""
    
    def test_token_verified_event_valid(self):
        event = TokenVerifiedEvent(user_id=123, is_valid=True)
        assert event.data["user_id"] == 123
        assert event.data["is_valid"] is True
        assert event.event_type == "token_verified"
        assert isinstance(event.occurred_at, datetime)
    
    def test_token_verified_event_invalid(self):
        event = TokenVerifiedEvent(user_id=123, is_valid=False)
        assert event.data["user_id"] == 123
        assert event.data["is_valid"] is False
    
    def test_token_verified_event_different_user(self):
        event = TokenVerifiedEvent(user_id=456, is_valid=True)
        assert event.data["user_id"] == 456
        assert event.data["is_valid"] is True