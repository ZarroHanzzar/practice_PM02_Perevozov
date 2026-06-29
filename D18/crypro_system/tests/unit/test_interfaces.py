# tests/unit/test_interfaces.py
"""
Unit tests for interfaces (абстрактные классы)
"""
import pytest
from abc import ABCMeta
from src.application.interfaces import (
    IPasswordService,
    ITokenService,
    IEncryptionService
)
from src.application.dto import PasswordDTO, PasswordHashDTO, TokenVerifyDTO


class TestInterfaces:
    """Тесты для интерфейсов"""
    
    def test_ipassword_service_is_abstract(self):
        """Проверка, что IPasswordService - абстрактный класс"""
        assert isinstance(IPasswordService, ABCMeta)
        assert hasattr(IPasswordService, 'hash_password')
        assert hasattr(IPasswordService, 'verify_password')
        # Проверяем, что методы абстрактные
        assert IPasswordService.hash_password.__isabstractmethod__ is True
        assert IPasswordService.verify_password.__isabstractmethod__ is True
    
    def test_itoken_service_is_abstract(self):
        """Проверка, что ITokenService - абстрактный класс"""
        assert isinstance(ITokenService, ABCMeta)
        assert hasattr(ITokenService, 'generate_token')
        assert hasattr(ITokenService, 'verify_token')
        assert ITokenService.generate_token.__isabstractmethod__ is True
        assert ITokenService.verify_token.__isabstractmethod__ is True
    
    def test_iencryption_service_is_abstract(self):
        """Проверка, что IEncryptionService - абстрактный класс"""
        assert isinstance(IEncryptionService, ABCMeta)
        assert hasattr(IEncryptionService, 'encrypt')
        assert hasattr(IEncryptionService, 'decrypt')
        assert IEncryptionService.encrypt.__isabstractmethod__ is True
        assert IEncryptionService.decrypt.__isabstractmethod__ is True
    
    def test_ipassword_service_methods_signature(self):
        """Проверка сигнатуры методов IPasswordService"""
        # Проверяем, что методы существуют с правильными именами
        assert callable(getattr(IPasswordService, 'hash_password', None))
        assert callable(getattr(IPasswordService, 'verify_password', None))
    
    def test_itoken_service_methods_signature(self):
        """Проверка сигнатуры методов ITokenService"""
        assert callable(getattr(ITokenService, 'generate_token', None))
        assert callable(getattr(ITokenService, 'verify_token', None))
    
    def test_iencryption_service_methods_signature(self):
        """Проверка сигнатуры методов IEncryptionService"""
        assert callable(getattr(IEncryptionService, 'encrypt', None))
        assert callable(getattr(IEncryptionService, 'decrypt', None))