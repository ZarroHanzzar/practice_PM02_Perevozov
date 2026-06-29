# tests/unit/test_external_api.py
"""
Unit tests for External API
"""
import pytest
import base64
from src.infrastructure.external_api import ExternalCryptoAPI


class TestExternalCryptoAPI:
    """Тесты для ExternalCryptoAPI"""
    
    def setup_method(self):
        self.api = ExternalCryptoAPI()
    
    def test_hash_password(self):
        """Тест хеширования пароля"""
        result = self.api.hash_password("my_password")
        assert 'hash' in result
        assert 'salt' in result
        assert len(result['hash']) == 64
        assert len(result['salt']) > 0
    
    def test_hash_password_with_salt(self):
        """Тест хеширования с солью"""
        salt = "fixed_salt_123"
        result = self.api.hash_password("my_password", salt)
        assert result['salt'] == salt
        assert len(result['hash']) == 64
    
    def test_hash_password_empty(self):
        """Тест хеширования пустого пароля"""
        result = self.api.hash_password("")
        assert 'hash' in result
        assert 'salt' in result
        assert len(result['hash']) == 64
    
    def test_verify_password_correct(self):
        """Тест проверки правильного пароля"""
        result = self.api.hash_password("my_password")
        assert self.api.verify_password("my_password", result['hash'], result['salt']) is True
    
    def test_verify_password_incorrect(self):
        """Тест проверки неправильного пароля"""
        result = self.api.hash_password("my_password")
        assert self.api.verify_password("wrong", result['hash'], result['salt']) is False
    
    def test_verify_password_empty(self):
        """Тест проверки пустого пароля"""
        result = self.api.hash_password("my_password")
        assert self.api.verify_password("", result['hash'], result['salt']) is False
    
    def test_generate_token(self):
        """Тест генерации токена"""
        token = self.api.generate_token(123)
        assert token is not None
        assert len(token) > 0
        
        # Проверяем, что можно декодировать
        decoded = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        assert '|' in decoded
    
    def test_generate_token_with_expiry(self):
        """Тест генерации токена с временем жизни"""
        token = self.api.generate_token(123, expires_in_hours=48)
        decoded = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        assert '|' in decoded
    
    def test_generate_token_user_id_zero(self):
        """Тест генерации токена с user_id = 0"""
        token = self.api.generate_token(0)
        decoded = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        assert '|' in decoded
    
    def test_generate_token_negative_user_id(self):
        """Тест генерации токена с отрицательным user_id"""
        token = self.api.generate_token(-1)
        decoded = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        assert '|' in decoded