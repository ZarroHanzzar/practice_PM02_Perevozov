# src/application/interfaces.py
"""
Abstract interfaces (Port-Adapter pattern)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .dto import PasswordDTO, PasswordHashDTO, TokenDTO, TokenVerifyDTO


class IPasswordService(ABC):
    """Интерфейс сервиса паролей"""
    
    @abstractmethod
    def hash_password(self, dto: PasswordDTO) -> PasswordHashDTO:
        """Хеширование пароля"""
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hash: str, salt: str) -> bool:
        """Проверка пароля"""
        pass


class ITokenService(ABC):
    """Интерфейс сервиса токенов"""
    
    @abstractmethod
    def generate_token(self, user_id: int, secret: str, expires_in_hours: int = 24) -> str:
        """Генерация токена"""
        pass
    
    @abstractmethod
    def verify_token(self, token: str, secret: str) -> TokenVerifyDTO:
        """Верификация токена"""
        pass


class IEncryptionService(ABC):
    """Интерфейс сервиса шифрования"""
    
    @abstractmethod
    def encrypt(self, data: str, key: str) -> str:
        """Шифрование данных"""
        pass
    
    @abstractmethod
    def decrypt(self, encrypted: str, key: str) -> str:
        """Дешифрование данных"""
        pass