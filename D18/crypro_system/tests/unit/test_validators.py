# tests/unit/test_validators.py (ДОБАВИТЬ В КОНЕЦ ФАЙЛА)
"""
Unit tests for validators
"""
import pytest
import base64
from src.utils.validators import PasswordValidator, TokenValidator, KeyValidator


class TestPasswordValidator:
    """Тесты для PasswordValidator"""
    
    def test_valid_password(self):
        is_valid, error = PasswordValidator.validate("Password123!")
        assert is_valid is True
        assert error is None
    
    def test_empty_password(self):
        is_valid, error = PasswordValidator.validate("")
        assert is_valid is False
        assert "cannot be empty" in error.lower()
    
    def test_too_short_password(self):
        is_valid, error = PasswordValidator.validate("Pass1!")
        assert is_valid is False
        assert "at least 8" in error.lower()
    
    def test_too_long_password(self):
        long_pass = "A" * 129 + "1!"
        is_valid, error = PasswordValidator.validate(long_pass)
        assert is_valid is False
        assert "at most 128" in error.lower()
    
    def test_no_digit(self):
        is_valid, error = PasswordValidator.validate("Password!")
        assert is_valid is False
        assert "digit" in error.lower()
    
    def test_no_lowercase(self):
        is_valid, error = PasswordValidator.validate("PASSWORD123!")
        assert is_valid is False
        assert "lowercase" in error.lower()
    
    def test_no_uppercase(self):
        is_valid, error = PasswordValidator.validate("password123!")
        assert is_valid is False
        assert "uppercase" in error.lower()
    
    def test_no_special(self):
        is_valid, error = PasswordValidator.validate("Password123")
        assert is_valid is False
        assert "special" in error.lower()
    
    def test_password_with_all_requirements(self):
        is_valid, error = PasswordValidator.validate("Test123!@#")
        assert is_valid is True
        assert error is None


class TestTokenValidator:
    """Тесты для TokenValidator"""
    
    def test_valid_token_format(self):
        token = base64.b64encode(b"valid_token").decode('utf-8')
        assert TokenValidator.validate_format(token) is True
    
    def test_empty_token(self):
        assert TokenValidator.validate_format("") is False
    
    def test_invalid_token(self):
        assert TokenValidator.validate_format("invalid!@#") is False
    
    def test_token_with_special_chars(self):
        assert TokenValidator.validate_format("token with spaces") is False


class TestKeyValidator:
    """Тесты для KeyValidator"""
    
    def test_valid_key(self):
        is_valid, error = KeyValidator.validate("valid_key_123")
        assert is_valid is True
        assert error is None
    
    def test_empty_key(self):
        is_valid, error = KeyValidator.validate("")
        assert is_valid is False
        assert "cannot be empty" in error.lower()
    
    def test_too_short_key(self):
        is_valid, error = KeyValidator.validate("short")
        assert is_valid is False
        assert "at least 8" in error.lower()
    
    def test_key_exact_min_length(self):
        is_valid, error = KeyValidator.validate("12345678")
        assert is_valid is True
        assert error is None
    
    def test_key_with_special_chars(self):
        is_valid, error = KeyValidator.validate("key!@#$%^&*")
        assert is_valid is True
        assert error is None