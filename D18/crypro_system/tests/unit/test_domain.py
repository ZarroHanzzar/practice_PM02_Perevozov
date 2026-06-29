# tests/unit/test_domain.py
"""
Unit tests for domain models
"""
import pytest
from datetime import datetime, timedelta
from src.core.domain import PasswordHash, Token, EncryptedData
from src.core.crypto import hash_password


class TestPasswordHash:
    """Тесты для PasswordHash"""
    
    def test_password_hash_creation(self):
        ph = PasswordHash(hash="abc123", salt="salt123")
        assert ph.hash == "abc123"
        assert ph.salt == "salt123"
        assert ph.algorithm == "sha256"
    
    def test_password_hash_verify(self):
        result = hash_password("my_password")
        ph = PasswordHash(hash=result['hash'], salt=result['salt'])
        assert ph.verify("my_password") is True
    
    def test_password_hash_verify_wrong(self):
        result = hash_password("my_password")
        ph = PasswordHash(hash=result['hash'], salt=result['salt'])
        assert ph.verify("wrong_password") is False
    
    def test_password_hash_custom_algorithm(self):
        ph = PasswordHash(hash="abc123", salt="salt123", algorithm="md5")
        assert ph.algorithm == "md5"


class TestToken:
    """Тесты для Token"""
    
    def test_token_creation(self):
        now = datetime.now()
        expires = now + timedelta(hours=24)
        token = Token(
            user_id=123,
            created_at=now,
            expires_at=expires,
            signature="sig123"
        )
        assert token.user_id == 123
        assert token.created_at == now
        assert token.expires_at == expires
        assert token.signature == "sig123"
    
    def test_token_is_expired(self):
        now = datetime.now()
        expired = now - timedelta(hours=1)
        token = Token(
            user_id=123,
            created_at=now,
            expires_at=expired,
            signature="sig123"
        )
        assert token.is_expired() is True
    
    def test_token_is_not_expired(self):
        now = datetime.now()
        future = now + timedelta(hours=24)
        token = Token(
            user_id=123,
            created_at=now,
            expires_at=future,
            signature="sig123"
        )
        assert token.is_expired() is False
    
    def test_token_is_valid(self):
        now = datetime.now()
        future = now + timedelta(hours=24)
        token = Token(
            user_id=123,
            created_at=now,
            expires_at=future,
            signature="sig123"
        )
        assert token.is_valid() is True
    
    def test_token_is_invalid(self):
        now = datetime.now()
        expired = now - timedelta(hours=1)
        token = Token(
            user_id=123,
            created_at=now,
            expires_at=expired,
            signature="sig123"
        )
        assert token.is_valid() is False


class TestEncryptedData:
    """Тесты для EncryptedData"""
    
    def test_encrypted_data_creation(self):
        ed = EncryptedData(data="encrypted_string")
        assert ed.data == "encrypted_string"
        assert ed.algorithm == "xor_base64"
        assert ed.key_hash is None
    
    def test_encrypted_data_with_key_hash(self):
        ed = EncryptedData(
            data="encrypted_string",
            algorithm="aes256",
            key_hash="hash123"
        )
        assert ed.algorithm == "aes256"
        assert ed.key_hash == "hash123"