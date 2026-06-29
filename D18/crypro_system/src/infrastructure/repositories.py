# src/infrastructure/repositories.py
"""
Repository implementations
"""
from typing import Dict, Optional, List
from datetime import datetime
import json

from ..core.domain import PasswordHash, Token, EncryptedData


class InMemoryRepository:
    """In-memory репозиторий для тестирования"""
    
    def __init__(self):
        self._data: Dict[str, any] = {}
    
    def save(self, key: str, value: any) -> None:
        self._data[key] = value
    
    def get(self, key: str) -> Optional[any]:
        return self._data.get(key)
    
    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False
    
    def list_all(self) -> List[any]:
        return list(self._data.values())
    
    def clear(self) -> None:
        self._data.clear()


class PasswordRepository(InMemoryRepository):
    """Репозиторий для паролей"""
    
    def save_password_hash(self, user_id: int, password_hash: PasswordHash) -> None:
        self.save(f"password_{user_id}", password_hash)
    
    def get_password_hash(self, user_id: int) -> Optional[PasswordHash]:
        return self.get(f"password_{user_id}")
    
    def delete_password_hash(self, user_id: int) -> bool:
        return self.delete(f"password_{user_id}")


class TokenRepository(InMemoryRepository):
    """Репозиторий для токенов"""
    
    def save_token(self, token: str, user_id: int, expires_at: datetime) -> None:
        self.save(f"token_{token}", {
            "user_id": user_id,
            "expires_at": expires_at.isoformat()
        })
    
    def get_token_data(self, token: str) -> Optional[Dict]:
        return self.get(f"token_{token}")
    
    def delete_token(self, token: str) -> bool:
        return self.delete(f"token_{token}")
    
    def cleanup_expired(self) -> int:
        """Удаление истекших токенов"""
        count = 0
        for key, value in list(self._data.items()):
            if key.startswith("token_"):
                expires_at = datetime.fromisoformat(value["expires_at"])
                if expires_at < datetime.now():
                    del self._data[key]
                    count += 1
        return count