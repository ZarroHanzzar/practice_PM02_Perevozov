# src/core/domain.py
"""
Domain models for cryptographic operations
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib


@dataclass
class PasswordHash:
    """Value Object для хеша пароля"""
    hash: str
    salt: str
    algorithm: str = "sha256"
    
    def verify(self, password: str) -> bool:
        """Проверка пароля"""
        import hmac
        from .crypto import hash_password
        result = hash_password(password, self.salt)
        return hmac.compare_digest(result['hash'], self.hash)


@dataclass
class Token:
    """Entity для токена аутентификации"""
    user_id: int
    created_at: datetime
    expires_at: datetime
    signature: str
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        return not self.is_expired()


@dataclass
class EncryptedData:
    """Value Object для зашифрованных данных"""
    data: str
    algorithm: str = "xor_base64"
    key_hash: Optional[str] = None