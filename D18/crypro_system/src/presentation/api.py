# src/presentation/api.py
"""
REST API for cryptographic operations
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import base64

from ..application.services import (
    PasswordService, TokenService, EncryptionService, HMACService
)
from ..application.dto import (
    PasswordDTO, EncryptDTO, DecryptDTO, HMACDTO
)


class CryptoAPI:
    """REST API для криптографических операций"""
    
    def __init__(self):
        self.password_service = PasswordService()
        self.token_service = TokenService()
        self.encryption_service = EncryptionService()
        self.hmac_service = HMACService()
    
    def hash_password_endpoint(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/crypto/hash"""
        try:
            password = request.get('password', '')
            salt = request.get('salt')
            
            dto = PasswordDTO(password=password, salt=salt)
            result = self.password_service.hash_password(dto)
            
            return {
                'status': 'success',
                'data': {
                    'hash': result.hash,
                    'salt': result.salt,
                    'algorithm': result.algorithm
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def verify_password_endpoint(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/crypto/verify"""
        try:
            password = request.get('password', '')
            hash_val = request.get('hash', '')
            salt = request.get('salt', '')
            
            is_valid = self.password_service.verify_password(password, hash_val, salt)
            
            return {
                'status': 'success',
                'data': {
                    'is_valid': is_valid
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def generate_token_endpoint(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/crypto/token"""
        try:
            user_id = request.get('user_id', 0)
            secret = request.get('secret', '')
            expires_in = request.get('expires_in_hours', 24)
            
            token = self.token_service.generate_token(user_id, secret, expires_in)
            
            return {
                'status': 'success',
                'data': {
                    'token': token,
                    'user_id': user_id,
                    'expires_in_hours': expires_in
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def verify_token_endpoint(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/crypto/verify-token"""
        try:
            token = request.get('token', '')
            secret = request.get('secret', '')
            
            result = self.token_service.verify_token(token, secret)
            
            return {
                'status': 'success',
                'data': {
                    'is_valid': result.is_valid,
                    'user_id': result.user_id,
                    'error': result.error
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def encrypt_endpoint(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/crypto/encrypt"""
        try:
            data = request.get('data', '')
            key = request.get('key', '')
            
            dto = EncryptDTO(data=data, key=key)
            encrypted = self.encryption_service.encrypt(dto)
            
            return {
                'status': 'success',
                'data': {
                    'encrypted': encrypted
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def decrypt_endpoint(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/crypto/decrypt"""
        try:
            encrypted = request.get('encrypted', '')
            key = request.get('key', '')
            
            dto = DecryptDTO(encrypted_data=encrypted, key=key)
            decrypted = self.encryption_service.decrypt(dto)
            
            return {
                'status': 'success',
                'data': {
                    'decrypted': decrypted
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }