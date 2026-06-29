# src/utils/validators.py
"""
Validators for cryptographic operations
"""
import re
import base64
from typing import Optional, Tuple


class PasswordValidator:
    """Валидатор паролей"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @classmethod
    def validate(cls, password: str) -> Tuple[bool, Optional[str]]:
        """Проверка пароля на соответствие требованиям"""
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"
        
        if len(password) > cls.MAX_LENGTH:
            return False, f"Password must be at most {cls.MAX_LENGTH} characters"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, None


class TokenValidator:
    """Валидатор токенов"""
    
    @classmethod
    def validate_format(cls, token: str) -> bool:
        """Проверка формата токена"""
        if not token:
            return False
        
        try:
            base64.b64decode(token.encode('utf-8'))
            return True
        except:
            return False


class KeyValidator:
    """Валидатор ключей"""
    
    MIN_LENGTH = 8
    
    @classmethod
    def validate(cls, key: str) -> Tuple[bool, Optional[str]]:
        """Проверка ключа"""
        if not key:
            return False, "Key cannot be empty"
        
        if len(key) < cls.MIN_LENGTH:
            return False, f"Key must be at least {cls.MIN_LENGTH} characters"
        
        return True, None