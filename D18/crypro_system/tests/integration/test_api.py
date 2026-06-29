# tests/integration/test_api.py
"""
Integration tests for API
"""
import pytest
from src.presentation.api import CryptoAPI


class TestCryptoAPI:
    """Тесты для CryptoAPI"""
    
    def setup_method(self):
        self.api = CryptoAPI()
    
    def test_hash_password_endpoint_success(self):
        request = {"password": "my_password"}
        response = self.api.hash_password_endpoint(request)
        
        assert response["status"] == "success"
        assert "hash" in response["data"]
        assert "salt" in response["data"]
    
    def test_hash_password_endpoint_empty(self):
        request = {"password": ""}
        response = self.api.hash_password_endpoint(request)
        
        assert response["status"] == "error"
    
    def test_verify_password_endpoint_success(self):
        # Сначала хешируем пароль
        hash_response = self.api.hash_password_endpoint(
            {"password": "my_password"}
        )
        hash_data = hash_response["data"]
        
        # Проверяем
        request = {
            "password": "my_password",
            "hash": hash_data["hash"],
            "salt": hash_data["salt"]
        }
        response = self.api.verify_password_endpoint(request)
        
        assert response["status"] == "success"
        assert response["data"]["is_valid"] is True
    
    def test_verify_password_endpoint_incorrect(self):
        request = {
            "password": "wrong_password",
            "hash": "fake_hash",
            "salt": "fake_salt"
        }
        response = self.api.verify_password_endpoint(request)
        
        assert response["status"] == "success"
        assert response["data"]["is_valid"] is False
    
    def test_generate_token_endpoint_success(self):
        request = {
            "user_id": 123,
            "secret": "secret_key",
            "expires_in_hours": 24
        }
        response = self.api.generate_token_endpoint(request)
        
        assert response["status"] == "success"
        assert "token" in response["data"]
        assert response["data"]["user_id"] == 123
    
    def test_generate_token_endpoint_invalid_user_id(self):
        request = {
            "user_id": -1,
            "secret": "secret_key"
        }
        response = self.api.generate_token_endpoint(request)
        
        assert response["status"] == "error"
    
    def test_verify_token_endpoint_success(self):
        # Генерируем токен
        token_response = self.api.generate_token_endpoint({
            "user_id": 123,
            "secret": "secret_key"
        })
        token = token_response["data"]["token"]
        
        # Проверяем
        request = {
            "token": token,
            "secret": "secret_key"
        }
        response = self.api.verify_token_endpoint(request)
        
        assert response["status"] == "success"
        assert response["data"]["is_valid"] is True
        assert response["data"]["user_id"] == 123
    
    def test_verify_token_endpoint_invalid(self):
        request = {
            "token": "invalid_token",
            "secret": "secret_key"
        }
        response = self.api.verify_token_endpoint(request)
        
        assert response["status"] == "success"
        assert response["data"]["is_valid"] is False
    
    def test_encrypt_decrypt_endpoint(self):
        # Шифруем
        encrypt_request = {
            "data": "Hello, World!",
            "key": "secret_key"
        }
        encrypt_response = self.api.encrypt_endpoint(encrypt_request)
        assert encrypt_response["status"] == "success"
        
        encrypted = encrypt_response["data"]["encrypted"]
        
        # Дешифруем
        decrypt_request = {
            "encrypted": encrypted,
            "key": "secret_key"
        }
        decrypt_response = self.api.decrypt_endpoint(decrypt_request)
        
        assert decrypt_response["status"] == "success"
        assert decrypt_response["data"]["decrypted"] == "Hello, World!"