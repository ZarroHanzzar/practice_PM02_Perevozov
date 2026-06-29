# tests/unit/test_services.py
"""
Unit tests for application services
"""
import pytest
from src.application.services import (
    PasswordService, TokenService, EncryptionService, HMACService
)
from src.application.dto import (
    PasswordDTO, EncryptDTO, DecryptDTO, HMACDTO
)
from src.core.exceptions import PasswordError, TokenError, EncryptionError


class TestPasswordService:
    """Тесты для PasswordService"""
    
    def test_hash_password(self):
        service = PasswordService()
        dto = PasswordDTO(password="my_password")
        result = service.hash_password(dto)
        
        assert result.hash is not None
        assert result.salt is not None
        assert result.algorithm == "sha256"
    
    def test_hash_password_empty(self):
        service = PasswordService()
        dto = PasswordDTO(password="")
        
        with pytest.raises(PasswordError):
            service.hash_password(dto)
    
    def test_hash_password_with_salt(self):
        service = PasswordService()
        dto = PasswordDTO(password="my_password", salt="fixed_salt")
        result = service.hash_password(dto)
        
        assert result.salt == "fixed_salt"
        assert result.hash is not None
    
    def test_verify_password_correct(self):
        service = PasswordService()
        dto = PasswordDTO(password="my_password")
        result = service.hash_password(dto)
        
        assert service.verify_password("my_password", result.hash, result.salt) is True
    
    def test_verify_password_incorrect(self):
        service = PasswordService()
        dto = PasswordDTO(password="my_password")
        result = service.hash_password(dto)
        
        assert service.verify_password("wrong", result.hash, result.salt) is False
    
    def test_verify_password_empty(self):
        service = PasswordService()
        dto = PasswordDTO(password="my_password")
        result = service.hash_password(dto)
        
        assert service.verify_password("", result.hash, result.salt) is False
    
    def test_verify_password_with_error(self):
        """Тест verify_password с ошибкой - передаем None значения"""
        service = PasswordService()
        result = service.verify_password(None, None, None)
        assert result is False


class TestTokenService:
    """Тесты для TokenService"""
    
    def test_generate_token(self):
        service = TokenService()
        token = service.generate_token(123, "secret")
        
        assert token is not None
        assert len(token) > 0
    
    def test_generate_token_invalid_user_id(self):
        service = TokenService()
        
        with pytest.raises(TokenError):
            service.generate_token(-1, "secret")
    
    def test_generate_token_zero_user_id(self):
        service = TokenService()
        
        with pytest.raises(TokenError):
            service.generate_token(0, "secret")
    
    def test_generate_token_empty_secret(self):
        service = TokenService()
        
        with pytest.raises(TokenError):
            service.generate_token(123, "")
    
    def test_verify_token_valid(self):
        service = TokenService()
        token = service.generate_token(123, "secret")
        result = service.verify_token(token, "secret")
        
        assert result.is_valid is True
        assert result.user_id == 123
        assert result.error is None
    
    def test_verify_token_invalid(self):
        service = TokenService()
        result = service.verify_token("invalid_token", "secret")
        
        assert result.is_valid is False
        assert result.user_id is None
        assert result.error == "Invalid token"
    
    def test_verify_token_wrong_secret(self):
        service = TokenService()
        token = service.generate_token(123, "secret")
        result = service.verify_token(token, "wrong_secret")
        
        assert result.is_valid is False
        assert result.user_id is None
    
    def test_verify_token_empty(self):
        service = TokenService()
        result = service.verify_token("", "secret")
        
        assert result.is_valid is False
        assert result.user_id is None


class TestEncryptionService:
    """Тесты для EncryptionService"""
    
    def test_encrypt_decrypt(self):
        service = EncryptionService()
        dto = EncryptDTO(data="Hello, World!", key="key")
        encrypted = service.encrypt(dto)
        
        decrypt_dto = DecryptDTO(encrypted_data=encrypted, key="key")
        decrypted = service.decrypt(decrypt_dto)
        
        assert decrypted == "Hello, World!"
    
    def test_encrypt_empty(self):
        service = EncryptionService()
        dto = EncryptDTO(data="", key="key")
        result = service.encrypt(dto)
        
        assert result == ""
    
    def test_encrypt_empty_key(self):
        service = EncryptionService()
        dto = EncryptDTO(data="data", key="")
        
        with pytest.raises(EncryptionError):
            service.encrypt(dto)
    
    def test_decrypt_empty(self):
        service = EncryptionService()
        dto = DecryptDTO(encrypted_data="", key="key")
        result = service.decrypt(dto)
        
        assert result == ""
    
    def test_decrypt_empty_key(self):
        service = EncryptionService()
        dto = DecryptDTO(encrypted_data="data", key="")
        
        with pytest.raises(EncryptionError):
            service.decrypt(dto)
    
    def test_encrypt_sensitive(self):
        service = EncryptionService()
        data = {"user": "John", "role": "admin"}
        encrypted = service.encrypt_sensitive(data, "key")
        decrypted = service.decrypt_sensitive(encrypted, "key")
        
        assert decrypted == data
    
    def test_encrypt_sensitive_empty(self):
        service = EncryptionService()
        data = {}
        encrypted = service.encrypt_sensitive(data, "key")
        decrypted = service.decrypt_sensitive(encrypted, "key")
        
        assert decrypted == {}
    
    def test_encrypt_sensitive_none(self):
        service = EncryptionService()
        encrypted = service.encrypt_sensitive(None, "key")
        decrypted = service.decrypt_sensitive(encrypted, "key")
        
        assert decrypted == {}
    
    def test_encrypt_sensitive_non_dict(self):
        service = EncryptionService()
        
        with pytest.raises(EncryptionError):
            service.encrypt_sensitive([1, 2, 3], "key")
    
    def test_encrypt_sensitive_error(self):
        """Тест encrypt_sensitive с ошибкой - пустой ключ"""
        service = EncryptionService()
        with pytest.raises(EncryptionError):
            service.encrypt_sensitive({"data": "test"}, "")
    
    def test_decrypt_sensitive_error(self):
        """Тест decrypt_sensitive с ошибкой - пустой ключ"""
        service = EncryptionService()
        with pytest.raises(EncryptionError):
            service.decrypt_sensitive("some_data", "")


class TestHMACService:
    """Тесты для HMACService"""
    
    def test_generate_hmac(self):
        service = HMACService()
        dto = HMACDTO(data="data", key="key")
        signature = service.generate(dto)
        
        assert signature is not None
        assert len(signature) > 0
        assert len(signature) == 64
    
    def test_generate_hmac_empty_data(self):
        service = HMACService()
        dto = HMACDTO(data="", key="key")
        signature = service.generate(dto)
        
        assert signature == "0" * 64
    
    def test_generate_hmac_empty_key(self):
        service = HMACService()
        dto = HMACDTO(data="data", key="")
        signature = service.generate(dto)
        assert signature is not None
        assert len(signature) == 64
    
    def test_verify_hmac_correct(self):
        service = HMACService()
        dto = HMACDTO(data="data", key="key")
        signature = service.generate(dto)
        
        verify_dto = HMACDTO(data="data", key="key", signature=signature)
        assert service.verify(verify_dto) is True
    
    def test_verify_hmac_incorrect(self):
        service = HMACService()
        verify_dto = HMACDTO(data="data", key="key", signature="wrong")
        
        assert service.verify(verify_dto) is False
    
    def test_verify_hmac_empty_signature(self):
        service = HMACService()
        verify_dto = HMACDTO(data="data", key="key", signature="")
        
        assert service.verify(verify_dto) is False
    
    def test_verify_hmac_empty_key(self):
        service = HMACService()
        verify_dto = HMACDTO(data="data", key="", signature="sig")
        result = service.verify(verify_dto)
        assert result is False
    
    def test_verify_hmac_with_error(self):
        """Тест verify HMAC с ошибкой - передаем None значения"""
        service = HMACService()
        dto = HMACDTO(data="", key="", signature="")
        result = service.verify(dto)
        assert result is False