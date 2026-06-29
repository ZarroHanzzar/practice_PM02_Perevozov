# src/infrastructure/external_api.py
"""
External API integrations
"""
from typing import Optional, Dict, Any
import requests
import hashlib
import hmac
import base64
import secrets
from datetime import datetime, timedelta


class ExternalCryptoAPI:
    """Внешний API для криптографических операций (заглушка)"""
    
    def __init__(self, base_url: str = "https://api.crypto.example.com"):
        self.base_url = base_url
        self._session = requests.Session()
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Хеширование пароля через внешний API"""
        if not salt:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.sha256()
        hash_obj.update(password.encode('utf-8'))
        hash_obj.update(salt.encode('utf-8'))
        
        return {
            'hash': hash_obj.hexdigest(),
            'salt': salt
        }
    
    def verify_password(self, password: str, hash_val: str, salt: str) -> bool:
        """Проверка пароля через внешний API"""
        result = self.hash_password(password, salt)
        return hmac.compare_digest(result['hash'], hash_val)
    
    def generate_token(self, user_id: int, expires_in_hours: int = 24) -> str:
        """Генерация токена через внешний API"""
        expiration = datetime.now() + timedelta(hours=expires_in_hours)
        token_data = f"{user_id}|{expiration.isoformat()}"
        return base64.b64encode(token_data.encode('utf-8')).decode('utf-8')