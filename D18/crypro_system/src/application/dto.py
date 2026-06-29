# src/application/dto.py
"""
Data Transfer Objects for cryptographic operations
"""
from dataclasses import dataclass
from typing import Optional, Any, Dict
from datetime import datetime


@dataclass
class PasswordDTO:
    """DTO для работы с паролями"""
    password: str
    salt: Optional[str] = None
    
    
@dataclass
class PasswordHashDTO:
    """DTO для результата хеширования пароля"""
    hash: str
    salt: str
    algorithm: str = "sha256"


@dataclass
class TokenDTO:
    """DTO для токена"""
    token: str
    user_id: int
    expires_at: datetime


@dataclass
class TokenVerifyDTO:
    """DTO для результата верификации токена"""
    is_valid: bool
    user_id: Optional[int] = None
    error: Optional[str] = None


@dataclass
class EncryptDTO:
    """DTO для шифрования"""
    data: str
    key: str


@dataclass
class DecryptDTO:
    """DTO для дешифрования"""
    encrypted_data: str
    key: str


@dataclass
class HMACDTO:
    """DTO для HMAC"""
    data: str
    key: str
    signature: Optional[str] = None