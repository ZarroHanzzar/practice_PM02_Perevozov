"""
Integration tests for repositories
"""
import pytest
from datetime import datetime, timedelta
from src.infrastructure.repositories import (
    PasswordRepository, TokenRepository, InMemoryRepository
)
from src.core.domain import PasswordHash, Token


class TestPasswordRepository:
    """Тесты для PasswordRepository"""
    
    def test_save_and_get(self):
        repo = PasswordRepository()
        password_hash = PasswordHash(
            hash="abc123",
            salt="salt123"
        )
        
        repo.save_password_hash(1, password_hash)
        result = repo.get_password_hash(1)
        
        assert result is not None
        assert result.hash == "abc123"
        assert result.salt == "salt123"
    
    def test_get_nonexistent(self):
        repo = PasswordRepository()
        result = repo.get_password_hash(999)
        assert result is None
    
    def test_delete(self):
        repo = PasswordRepository()
        password_hash = PasswordHash(hash="abc123", salt="salt123")
        repo.save_password_hash(1, password_hash)
        
        assert repo.delete_password_hash(1) is True
        assert repo.get_password_hash(1) is None
    
    def test_clear(self):
        repo = PasswordRepository()
        repo.save_password_hash(1, PasswordHash(hash="abc", salt="def"))
        repo.save_password_hash(2, PasswordHash(hash="ghi", salt="jkl"))
        
        assert len(repo.list_all()) == 2
        repo.clear()
        assert len(repo.list_all()) == 0


class TestTokenRepository:
    """Тесты для TokenRepository"""
    
    def test_save_and_get(self):
        repo = TokenRepository()
        expires_at = datetime.now() + timedelta(hours=24)
        
        repo.save_token("token123", 1, expires_at)
        result = repo.get_token_data("token123")
        
        assert result is not None
        assert result["user_id"] == 1
        assert datetime.fromisoformat(result["expires_at"]) == expires_at
    
    def test_get_nonexistent(self):
        repo = TokenRepository()
        result = repo.get_token_data("nonexistent")
        assert result is None
    
    def test_cleanup_expired(self):
        repo = TokenRepository()
        
        # Создаем истекший токен
        expired = datetime.now() - timedelta(hours=1)
        repo.save_token("expired", 1, expired)
        
        # Создаем валидный токен
        valid = datetime.now() + timedelta(hours=24)
        repo.save_token("valid", 2, valid)
        
        assert repo.cleanup_expired() == 1
        assert repo.get_token_data("expired") is None
        assert repo.get_token_data("valid") is not None