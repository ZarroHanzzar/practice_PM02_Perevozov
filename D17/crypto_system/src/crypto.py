"""
Модуль для хеширования и шифрования данных в системе бронирования.
"""

import hashlib
import base64
import binascii
from typing import Optional, Dict, Any
import json
import os
import secrets
import string
import hmac
from cryptography.fernet import Fernet


class CryptoService:
    """Сервис для шифрования и хеширования данных."""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Инициализация сервиса шифрования.
        """
        if secret_key is None:
            secret_key = os.environ.get(
                'CRYPTO_SECRET',
                'default_secret_key_32_bytes_long_12345'
            )

        if len(secret_key) < 32:
            raise ValueError(
                "Secret key must be at least 32 characters long"
            )

        self.secret_key = secret_key
        self._fernet: Optional[Fernet] = None
        self._init_fernet()

    def _init_fernet(self) -> None:
        """Инициализация Fernet для симметричного шифрования."""
        key = base64.urlsafe_b64encode(self.secret_key.encode()[:32])
        self._fernet = Fernet(key)

    def hash_password(
        self,
        password: str,
        salt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Хеширование пароля с солью.
        """
        if not password:
            raise ValueError("Password cannot be empty")

        if salt is None:
            salt = os.urandom(16).hex()

        kdf = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        hashed = kdf.hex()

        return {
            'hash': hashed,
            'salt': salt,
            'algorithm': 'pbkdf2_sha256'
        }

    def verify_password(
        self,
        password: str,
        stored_hash: str,
        salt: str
    ) -> bool:
        """
        Проверка пароля.
        """
        if not password or not stored_hash or not salt:
            return False

        result = self.hash_password(password, salt)
        return hmac.compare_digest(result['hash'], stored_hash)

    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """
        Шифрование данных.
        """
        if not data:
            data = {}

        json_data = json.dumps(data, ensure_ascii=False)
        if self._fernet is None:
            raise RuntimeError("Fernet not initialized")
        encrypted = self._fernet.encrypt(json_data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Дешифрование данных.
        """
        try:
            decoded = base64.urlsafe_b64decode(
                encrypted_data.encode('utf-8')
            )
            if self._fernet is None:
                raise RuntimeError("Fernet not initialized")
            decrypted = self._fernet.decrypt(decoded)
            return json.loads(decrypted.decode('utf-8'))
        except (binascii.Error, json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")

    def hash_string(self, text: str, algorithm: str = 'sha256') -> str:
        """
        Хеширование строки.
        """
        supported_algorithms = {
            'sha256': hashlib.sha256,
            'sha1': hashlib.sha1,
            'sha512': hashlib.sha512,
            'md5': hashlib.md5,
        }

        if algorithm not in supported_algorithms:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Supported: {list(supported_algorithms.keys())}"
            )

        return supported_algorithms[algorithm](
            text.encode('utf-8')
        ).hexdigest()

    def generate_api_key(self, user_id: int) -> str:
        """
        Генерация API ключа.
        """
        alphabet = string.ascii_letters + string.digits + "-"
        random_part = ''.join(
            secrets.choice(alphabet) for _ in range(32)
        )
        return f"api_{user_id}_{random_part}"

    def secure_compare(self, str1: str, str2: str) -> bool:
        """
        Безопасное сравнение строк.
        """
        return hmac.compare_digest(
            str1.encode('utf-8'),
            str2.encode('utf-8')
        )

    def hash_file(self, file_content: bytes) -> str:
        """
        Хеширование содержимого файла.
        """
        if not file_content:
            return hashlib.sha256(b'').hexdigest()
        return hashlib.sha256(file_content).hexdigest()

    def hash_with_unicode(self, text: str) -> str:
        """
        Хеширование текста с Unicode символами.
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
