# src/application/services.py
"""
Application services (CQRS: Commands and Queries)
"""
from typing import Optional, Dict, Any
from datetime import datetime
import hmac
import base64

from ..core.crypto import (
    hash_password as core_hash_password,
    verify_password as core_verify_password,
    generate_token as core_generate_token,
    verify_token as core_verify_token,
    generate_hmac as core_generate_hmac,
    verify_hmac as core_verify_hmac,
    encrypt_data as core_encrypt_data,
    decrypt_data as core_decrypt_data,
    encrypt_sensitive_data as core_encrypt_sensitive,
    decrypt_sensitive_data as core_decrypt_sensitive
)
from ..core.exceptions import (
    PasswordError, TokenError, EncryptionError, 
    InvalidPasswordError, ExpiredTokenError
)
from ..core.events import (
    PasswordHashedEvent, TokenGeneratedEvent, TokenVerifiedEvent
)
from .dto import (
    PasswordDTO, PasswordHashDTO, TokenDTO, TokenVerifyDTO,
    EncryptDTO, DecryptDTO, HMACDTO
)


class PasswordService:
    """Сервис для работы с паролями"""
    
    @staticmethod
    def hash_password(dto: PasswordDTO) -> PasswordHashDTO:
        """Хеширование пароля"""
        try:
            result = core_hash_password(dto.password, dto.salt)
            
            # Генерируем событие
            event = PasswordHashedEvent(0, "sha256")
            
            return PasswordHashDTO(
                hash=result['hash'],
                salt=result['salt'],
                algorithm="sha256"
            )
        except Exception as e:
            raise PasswordError(f"Failed to hash password: {e}")
    
    @staticmethod
    def verify_password(password: str, hash_val: str, salt: str) -> bool:
        """Проверка пароля"""
        try:
            if password is None or hash_val is None or salt is None:
                return False
            return core_verify_password(password, hash_val, salt)
        except Exception as e:
            raise PasswordError(f"Failed to verify password: {e}")


class TokenService:
    """Сервис для работы с токенами"""
    
    @staticmethod
    def generate_token(user_id: int, secret: str, expires_in_hours: int = 24) -> str:
        """Генерация токена"""
        try:
            token = core_generate_token(user_id, secret, expires_in_hours)
            
            # Генерируем событие
            event = TokenGeneratedEvent(user_id, expires_in_hours)
            
            return token
        except Exception as e:
            raise TokenError(f"Failed to generate token: {e}")
    
    @staticmethod
    def verify_token(token: str, secret: str) -> TokenVerifyDTO:
        """Верификация токена"""
        try:
            user_id = core_verify_token(token, secret)
            
            if user_id is None:
                return TokenVerifyDTO(is_valid=False, error="Invalid token")
            
            # Верификация прошла успешно
            event = TokenVerifiedEvent(user_id, True)
            
            return TokenVerifyDTO(is_valid=True, user_id=user_id)
        except Exception as e:
            return TokenVerifyDTO(is_valid=False, error=str(e))


class EncryptionService:
    """Сервис для шифрования"""
    
    @staticmethod
    def encrypt(dto: EncryptDTO) -> str:
        """Шифрование данных"""
        try:
            return core_encrypt_data(dto.data, dto.key)
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt data: {e}")
    
    @staticmethod
    def decrypt(dto: DecryptDTO) -> str:
        """Дешифрование данных"""
        try:
            return core_decrypt_data(dto.encrypted_data, dto.key)
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt data: {e}")
    
    @staticmethod
    def encrypt_sensitive(data: Dict[str, Any], key: str) -> str:
        """Шифрование структурированных данных"""
        try:
            return core_encrypt_sensitive(data, key)
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt sensitive data: {e}")
    
    @staticmethod
    def decrypt_sensitive(encrypted: str, key: str) -> Dict[str, Any]:
        """Дешифрование структурированных данных"""
        try:
            return core_decrypt_sensitive(encrypted, key)
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt sensitive data: {e}")


class HMACService:
    """Сервис для работы с HMAC"""
    
    @staticmethod
    def generate(dto: HMACDTO) -> str:
        """Генерация HMAC"""
        try:
            return core_generate_hmac(dto.data, dto.key)
        except Exception as e:
            raise EncryptionError(f"Failed to generate HMAC: {e}")
    
    @staticmethod
    def verify(dto: HMACDTO) -> bool:
        """Проверка HMAC"""
        try:
            if dto.signature is None:
                return False
            return core_verify_hmac(dto.data, dto.signature, dto.key)
        except Exception as e:
            raise EncryptionError(f"Failed to verify HMAC: {e}")