# src/core/events.py
"""
Domain Events for cryptographic operations
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class DomainEvent:
    """Базовый класс для доменных событий"""
    occurred_at: datetime
    event_type: str
    data: Dict[str, Any]


@dataclass
class PasswordHashedEvent(DomainEvent):
    """Событие хеширования пароля"""
    user_id: int
    algorithm: str
    
    def __init__(self, user_id: int, algorithm: str):
        super().__init__(
            occurred_at=datetime.now(),
            event_type="password_hashed",
            data={"user_id": user_id, "algorithm": algorithm}
        )
        self.user_id = user_id
        self.algorithm = algorithm


@dataclass
class TokenGeneratedEvent(DomainEvent):
    """Событие генерации токена"""
    user_id: int
    expires_in_hours: int
    
    def __init__(self, user_id: int, expires_in_hours: int):
        super().__init__(
            occurred_at=datetime.now(),
            event_type="token_generated",
            data={"user_id": user_id, "expires_in_hours": expires_in_hours}
        )
        self.user_id = user_id
        self.expires_in_hours = expires_in_hours


@dataclass
class TokenVerifiedEvent(DomainEvent):
    """Событие верификации токена"""
    user_id: int
    is_valid: bool
    
    def __init__(self, user_id: int, is_valid: bool):
        super().__init__(
            occurred_at=datetime.now(),
            event_type="token_verified",
            data={"user_id": user_id, "is_valid": is_valid}
        )
        self.user_id = user_id
        self.is_valid = is_valid