# tests/unit/test_crypto.py
"""
Unit tests for cryptographic operations
"""
import pytest
import base64
from src.core.crypto import (
    hash_password,
    verify_password,
    encrypt_data,
    decrypt_data,
    generate_token,
    verify_token,
    generate_hmac,
    verify_hmac,
    encrypt_sensitive_data,
    decrypt_sensitive_data
)


# ===================================================================
# ТЕСТЫ ДЛЯ hash_password
# ===================================================================

def test_hash_password_basic():
    """Базовое хеширование пароля"""
    result = hash_password("my_password")
    assert 'hash' in result
    assert 'salt' in result
    assert len(result['hash']) > 0
    assert len(result['salt']) > 0


def test_hash_password_same_password_different_salt():
    """Одинаковые пароли с разными солями дают разные хеши"""
    result1 = hash_password("my_password")
    result2 = hash_password("my_password")
    
    assert result1['hash'] != result2['hash']
    assert result1['salt'] != result2['salt']


def test_hash_password_with_provided_salt():
    """Хеширование с предоставленной солью"""
    salt = "fixed_salt_123"
    result = hash_password("my_password", salt)
    
    assert result['salt'] == salt
    assert len(result['hash']) > 0


def test_hash_password_empty_raises_error():
    """Хеширование пустого пароля вызывает ошибку"""
    with pytest.raises(ValueError, match="Password cannot be empty"):
        hash_password("")


def test_hash_password_unicode():
    """Хеширование пароля с Unicode символами"""
    result = hash_password("пароль_с_unicode_🔐")
    assert 'hash' in result
    assert 'salt' in result
    assert len(result['hash']) == 64


def test_hash_password_very_long():
    """Хеширование очень длинного пароля"""
    long_password = "a" * 10000
    result = hash_password(long_password)
    assert len(result['hash']) == 64


# ===================================================================
# ТЕСТЫ ДЛЯ verify_password
# ===================================================================

def test_verify_password_correct():
    """Проверка правильного пароля"""
    result = hash_password("my_password")
    assert verify_password("my_password", result['hash'], result['salt']) is True


def test_verify_password_incorrect():
    """Проверка неправильного пароля"""
    result = hash_password("my_password")
    assert verify_password("wrong_password", result['hash'], result['salt']) is False


def test_verify_password_with_none():
    """Проверка с None значениями"""
    assert verify_password(None, "hash", "salt") is False
    assert verify_password("pass", None, "salt") is False
    assert verify_password("pass", "hash", None) is False


def test_verify_password_empty():
    """Проверка с пустыми значениями"""
    result = hash_password("my_password")
    assert verify_password("", result['hash'], result['salt']) is False
    assert verify_password("my_password", "", result['salt']) is False
    assert verify_password("my_password", result['hash'], "") is False


# ===================================================================
# ТЕСТЫ ДЛЯ encrypt_data / decrypt_data
# ===================================================================

def test_encrypt_decrypt_basic():
    """Базовое шифрование и дешифрование"""
    original = "Hello, World!"
    encrypted = encrypt_data(original, "key")
    decrypted = decrypt_data(encrypted, "key")
    assert decrypted == original


def test_encrypt_empty_string():
    """Шифрование пустой строки"""
    result = encrypt_data("", "key")
    assert result == ""


def test_decrypt_empty_string():
    """Дешифрование пустой строки"""
    result = decrypt_data("", "key")
    assert result == ""


def test_encrypt_data_empty_key():
    """Шифрование с пустым ключом"""
    with pytest.raises(ValueError, match="Key cannot be empty"):
        encrypt_data("data", "")


def test_encrypt_data_unicode():
    """Шифрование данных с Unicode символами"""
    original = "Привет, мир! 🌍"
    encrypted = encrypt_data(original, "key")
    decrypted = decrypt_data(encrypted, "key")
    assert decrypted == original


# ===================================================================
# ТЕСТЫ ДЛЯ generate_token / verify_token
# ===================================================================

def test_generate_verify_token():
    """Генерация и верификация токена"""
    token = generate_token(123, "secret_key")
    user_id = verify_token(token, "secret_key")
    assert user_id == 123


def test_generate_token_for_user_1():
    """Токен для пользователя с ID=1"""
    token = generate_token(1, "secret")
    user_id = verify_token(token, "secret")
    assert user_id == 1


def test_generate_token_negative_user_id():
    """Генерация токена с отрицательным user_id"""
    with pytest.raises(ValueError, match="User ID must be positive"):
        generate_token(-1, "secret")


def test_generate_token_zero_user_id():
    """Генерация токена с user_id = 0"""
    with pytest.raises(ValueError, match="User ID must be positive"):
        generate_token(0, "secret")


def test_generate_token_empty_secret():
    """Генерация токена с пустым секретом"""
    with pytest.raises(ValueError, match="Secret cannot be empty"):
        generate_token(1, "")


def test_verify_token_invalid():
    """Проверка невалидного токена"""
    result = verify_token("invalid_token", "secret")
    assert result is None


def test_verify_token_expired():
    """Проверка истекшего токена"""
    token = generate_token(1, "secret", expires_in_hours=-1)
    result = verify_token(token, "secret")
    assert result is None


# ===================================================================
# ТЕСТЫ ДЛЯ generate_hmac / verify_hmac
# ===================================================================

def test_generate_verify_hmac():
    """Генерация и верификация HMAC"""
    data = "important_data"
    key = "secret_key"
    signature = generate_hmac(data, key)
    assert verify_hmac(data, signature, key) is True


def test_hmac_incorrect_signature():
    """Проверка с неправильной подписью"""
    data = "important_data"
    key = "secret_key"
    signature = generate_hmac(data, key)
    assert verify_hmac(data, signature + "x", key) is False


def test_generate_hmac_empty_data():
    """Генерация HMAC для пустых данных"""
    signature = generate_hmac("", "key")
    assert signature == "0" * 64
    assert verify_hmac("", signature, "key") is True


def test_generate_hmac_unicode():
    """Генерация HMAC для данных с Unicode"""
    data = "Привет, мир! 🌍"
    key = "ключ_🔐"
    signature = generate_hmac(data, key)
    assert verify_hmac(data, signature, key) is True


def test_verify_hmac_case_sensitive():
    """Проверка HMAC с учетом регистра"""
    data = "test"
    key = "key"
    signature = generate_hmac(data, key)
    assert verify_hmac(data, signature.upper(), key) is False


# ===================================================================
# ТЕСТЫ ДЛЯ encrypt_sensitive_data / decrypt_sensitive_data
# ===================================================================

def test_encrypt_decrypt_sensitive_data():
    """Шифрование и дешифрование структурированных данных"""
    data = {
        "user_id": 123,
        "email": "user@example.com",
        "role": "admin"
    }
    encrypted = encrypt_sensitive_data(data, "key")
    decrypted = decrypt_sensitive_data(encrypted, "key")
    assert decrypted == data


def test_encrypt_sensitive_data_empty():
    """Шифрование пустых структурированных данных"""
    data = {}
    encrypted = encrypt_sensitive_data(data, "key")
    decrypted = decrypt_sensitive_data(encrypted, "key")
    assert decrypted == {}


def test_encrypt_sensitive_data_with_none():
    """Шифрование с None"""
    result = encrypt_sensitive_data(None, "key")
    decrypted = decrypt_sensitive_data(result, "key")
    assert decrypted == {}


def test_encrypt_sensitive_data_non_dict():
    """Шифрование с не-словарём"""
    with pytest.raises(TypeError, match="Data must be a dictionary"):
        encrypt_sensitive_data([1, 2, 3], "key")


def test_encrypt_sensitive_data_unicode_keys():
    """Шифрование данных с Unicode ключами и значениями"""
    data = {
        "пользователь": "Алексей",
        "роль": "администратор",
        "настройки": {"тема": "тёмная"}
    }
    encrypted = encrypt_sensitive_data(data, "key")
    decrypted = decrypt_sensitive_data(encrypted, "key")
    assert decrypted == data