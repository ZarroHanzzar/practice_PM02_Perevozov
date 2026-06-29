# src/core/crypto.py
"""
Модуль для криптографических операций в системе бронирования

ИСПРАВЛЕННАЯ ВЕРСИЯ - все дефекты устранены
"""
import hashlib
import base64
from typing import Optional, Dict, Any
import hmac
import secrets
from datetime import datetime, timedelta
import json


def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    """
    Хеширование пароля с солью.
    
    Правила:
    - Использование SHA-256 (безопасный алгоритм)
    - Поддержка Unicode (UTF-8)
    - Обработка пустых строк
    - Генерация случайной соли если не предоставлена
    
    Args:
        password: Пароль для хеширования
        salt: Соль (опционально, генерируется автоматически)
    
    Returns:
        Словарь с хешем и солью
    
    Raises:
        ValueError: Если пароль пустой
    """
    # ИСПРАВЛЕНО: Проверка на пустую строку
    if not password:
        raise ValueError("Password cannot be empty")
    
    if not salt:
        salt = secrets.token_hex(16)
    
    # ИСПРАВЛЕНО: Использование SHA-256 вместо MD5
    # ИСПРАВЛЕНО: Поддержка Unicode через UTF-8
    hash_obj = hashlib.sha256()
    hash_obj.update(password.encode('utf-8'))
    hash_obj.update(salt.encode('utf-8'))
    
    return {
        'hash': hash_obj.hexdigest(),
        'salt': salt
    }


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """
    Проверка пароля.
    
    Args:
        password: Пароль для проверки
        stored_hash: Сохраненный хеш
        salt: Соль использованная при хешировании
    
    Returns:
        True если пароль верный, иначе False
    
    ИСПРАВЛЕНО:
    - Использование compare_digest для защиты от timing attack
    - Проверка входных данных на None
    """
    # ИСПРАВЛЕНО: Проверка входных данных
    if password is None or stored_hash is None or salt is None:
        return False
    if not password or not stored_hash or not salt:
        return False
    
    result = hash_password(password, salt)
    
    # ИСПРАВЛЕНО: Использование compare_digest
    return hmac.compare_digest(result['hash'], stored_hash)


def encrypt_data(data: str, key: str) -> str:
    """
    Шифрование данных.
    
    Используется XOR шифрование с SHA-256 ключом для демонстрации.
    В реальном проекте рекомендуется использовать AES-GCM.
    
    Args:
        data: Данные для шифрования
        key: Ключ шифрования
    
    Returns:
        Зашифрованные данные в формате base64
    
    Raises:
        ValueError: Если ключ пустой
    """
    if not data:
        return ""
    
    # ИСПРАВЛЕНО: Проверка ключа
    if not key:
        raise ValueError("Key cannot be empty")
    
    # ИСПРАВЛЕНО: Настоящее шифрование вместо base64
    key_bytes = hashlib.sha256(key.encode('utf-8')).digest()
    data_bytes = data.encode('utf-8')
    
    # XOR шифрование с повторяющимся ключом
    encrypted_bytes = bytes([
        data_bytes[i] ^ key_bytes[i % len(key_bytes)] 
        for i in range(len(data_bytes))
    ])
    
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def decrypt_data(encrypted: str, key: str) -> str:
    """
    Дешифрование данных.
    
    Args:
        encrypted: Зашифрованные данные в формате base64
        key: Ключ шифрования
    
    Returns:
        Расшифрованные данные
    
    Raises:
        ValueError: Если ключ пустой или данные повреждены
    """
    if not encrypted:
        return ""
    
    # ИСПРАВЛЕНО: Проверка ключа
    if not key:
        raise ValueError("Key cannot be empty")
    
    try:
        key_bytes = hashlib.sha256(key.encode('utf-8')).digest()
        encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
        
        # XOR дешифрование
        decrypted_bytes = bytes([
            encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)] 
            for i in range(len(encrypted_bytes))
        ])
        
        return decrypted_bytes.decode('utf-8')
    
    except base64.binascii.Error as e:
        raise ValueError(f"Invalid base64 data: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid decoded data: {e}")
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")


def generate_hmac(data: str, key: str) -> str:
    """
    Генерация HMAC для данных.
    
    Args:
        data: Данные для подписи
        key: Секретный ключ
    
    Returns:
        HMAC подпись в hex формате
    
    ИСПРАВЛЕНО:
    - Обработка пустых данных
    - Поддержка Unicode через UTF-8
    - Обработка пустого ключа
    """
    # ИСПРАВЛЕНО: Обработка пустых данных
    if not data:
        return "0" * 64
    
    # ИСПРАВЛЕНО: Если ключ пустой, используем пустой байтовый объект
    key_bytes = key.encode('utf-8') if key else b''
    
    # ИСПРАВЛЕНО: Поддержка Unicode через UTF-8
    hmac_obj = hmac.new(
        key_bytes,
        data.encode('utf-8'),
        hashlib.sha256
    )
    return hmac_obj.hexdigest()


def verify_hmac(data: str, signature: str, key: str) -> bool:
    """
    Проверка HMAC.
    
    Args:
        data: Данные для проверки
        signature: Подпись для проверки
        key: Секретный ключ
    
    Returns:
        True если подпись верная, иначе False
    
    ИСПРАВЛЕНО:
    - Использование compare_digest для защиты от timing attack
    - Проверка signature на None
    """
    # ИСПРАВЛЕНО: Проверка signature на None
    if signature is None:
        return False
    
    expected = generate_hmac(data, key)
    # ИСПРАВЛЕНО: Использование compare_digest
    return hmac.compare_digest(expected, signature)


def generate_token(user_id: int, secret: str, expires_in_hours: int = 24) -> str:
    """
    Генерация токена для аутентификации.
    
    Токен содержит:
    - ID пользователя
    - Время истечения
    - HMAC подпись для верификации
    
    Args:
        user_id: ID пользователя
        secret: Секретный ключ для подписи
        expires_in_hours: Время жизни токена в часах
    
    Returns:
        Токен в формате base64
    
    Raises:
        ValueError: Если user_id не положительный или secret пустой
    
    ИСПРАВЛЕНО:
    - Проверка user_id
    - Использование HMAC подписи
    """
    # ИСПРАВЛЕНО: Проверка user_id
    if user_id <= 0:
        raise ValueError("User ID must be positive")
    if not secret:
        raise ValueError("Secret cannot be empty")
    
    expiration = datetime.now() + timedelta(hours=expires_in_hours)
    
    # ИСПРАВЛЕНО: Добавлена HMAC подпись
    # Используем '|' как разделитель для избежания конфликта с ISO форматом
    data = f"{user_id}|{expiration.isoformat()}"
    signature = generate_hmac(data, secret)
    token_data = f"{data}|{signature}"
    
    return base64.b64encode(token_data.encode('utf-8')).decode('utf-8')


def verify_token(token: str, secret: str) -> Optional[int]:
    """
    Верификация токена.
    
    Args:
        token: Токен для проверки
        secret: Секретный ключ
    
    Returns:
        ID пользователя если токен валидный, иначе None
    
    ИСПРАВЛЕНО:
    - Проверка подписи
    - Проверка срока действия
    - Обработка ошибок декодирования
    """
    if not token or not secret:
        return None
    
    try:
        decoded = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        # ИСПРАВЛЕНО: Используем '|' как разделитель
        parts = decoded.split('|')
        
        # ИСПРАВЛЕНО: Проверка формата
        if len(parts) != 3:
            return None
        
        user_id_str, expiration_str, signature = parts
        user_id = int(user_id_str)
        
        # ИСПРАВЛЕНО: Проверка подписи
        data = f"{user_id}|{expiration_str}"
        if not verify_hmac(data, signature, secret):
            return None
        
        # ИСПРАВЛЕНО: Проверка срока действия
        expiration = datetime.fromisoformat(expiration_str)
        if expiration < datetime.now():
            return None
        
        return user_id
    
    except (ValueError, TypeError, base64.binascii.Error):
        return None


def encrypt_sensitive_data(data: Dict[str, Any], key: str) -> str:
    """
    Шифрование структурированных данных.
    
    Args:
        data: Словарь с данными для шифрования
        key: Ключ шифрования
    
    Returns:
        Зашифрованные данные в формате base64
    
    Raises:
        TypeError: Если data не является словарем
        ValueError: Если ключ пустой
    
    ИСПРАВЛЕНО:
    - Обработка None значений
    - Проверка типа данных
    """
    # ИСПРАВЛЕНО: Обработка None значений
    if data is None:
        data = {}
    
    # ИСПРАВЛЕНО: Проверка типа данных
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    
    json_str = json.dumps(data, ensure_ascii=False)
    return encrypt_data(json_str, key)


def decrypt_sensitive_data(encrypted: str, key: str) -> Dict[str, Any]:
    """
    Дешифрование структурированных данных.
    
    Args:
        encrypted: Зашифрованные данные в формате base64
        key: Ключ шифрования
    
    Returns:
        Расшифрованный словарь с данными
    
    Raises:
        ValueError: Если данные повреждены или JSON некорректен
    
    ИСПРАВЛЕНО:
    - Обработка пустой строки
    - Обработка ошибок JSON с информативным сообщением
    """
    # ИСПРАВЛЕНО: Обработка пустой строки
    if not encrypted:
        return {}
    
    try:
        decrypted = decrypt_data(encrypted, key)
        if not decrypted:
            return {}
        
        # ИСПРАВЛЕНО: Обработка ошибок JSON
        return json.loads(decrypted)
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data after decryption: {e}")
    except ValueError as e:
        raise


# ===================================================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ УЛУЧШЕНИЯ ФУНКЦИОНАЛЬНОСТИ
# ===================================================================

def generate_secure_random_string(length: int = 32) -> str:
    """
    Генерация безопасной случайной строки.
    
    Args:
        length: Длина строки в байтах
    
    Returns:
        Случайная строка в hex формате
    """
    return secrets.token_hex(length)


def hash_password_with_pepper(password: str, pepper: str, salt: Optional[str] = None) -> Dict[str, str]:
    """
    Хеширование пароля с дополнительным pepper (секретным ключом).
    
    Pepper добавляет дополнительный уровень безопасности.
    
    Args:
        password: Пароль для хеширования
        pepper: Секретный pepper (хранится отдельно от базы)
        salt: Соль (опционально)
    
    Returns:
        Словарь с хешем и солью
    """
    if not password:
        raise ValueError("Password cannot be empty")
    if not pepper:
        raise ValueError("Pepper cannot be empty")
    
    if not salt:
        salt = secrets.token_hex(16)
    
    # Хешируем пароль с солью и pepper
    hash_obj = hashlib.sha256()
    hash_obj.update(password.encode('utf-8'))
    hash_obj.update(salt.encode('utf-8'))
    hash_obj.update(pepper.encode('utf-8'))
    
    return {
        'hash': hash_obj.hexdigest(),
        'salt': salt
    }


def generate_api_key(prefix: str = "sk") -> str:
    """
    Генерация API ключа.
    
    Args:
        prefix: Префикс ключа (например, "sk" для secret key)
    
    Returns:
        API ключ в формате prefix_ + случайная строка
    """
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"


def hash_file_content(content: bytes) -> str:
    """
    Хеширование содержимого файла.
    
    Args:
        content: Содержимое файла в байтах
    
    Returns:
        SHA-256 хеш в hex формате
    """
    if not content:
        raise ValueError("Content cannot be empty")
    
    hash_obj = hashlib.sha256()
    hash_obj.update(content)
    return hash_obj.hexdigest()


def is_password_strong(password: str) -> bool:
    """
    Проверка сложности пароля.
    
    Требования:
    - Минимум 8 символов
    - Содержит цифры
    - Содержит буквы в разных регистрах
    - Содержит спецсимволы
    
    Args:
        password: Пароль для проверки
    
    Returns:
        True если пароль сложный, иначе False
    """
    import re
    
    if len(password) < 8:
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True


def get_password_strength(password: str) -> Dict[str, Any]:
    """
    Анализ сложности пароля с детальной информацией.
    
    Args:
        password: Пароль для анализа
    
    Returns:
        Словарь с деталями сложности
    """
    import re
    
    result = {
        'length': len(password),
        'has_digit': bool(re.search(r'\d', password)),
        'has_lowercase': bool(re.search(r'[a-z]', password)),
        'has_uppercase': bool(re.search(r'[A-Z]', password)),
        'has_special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
        'is_strong': False
    }
    
    # Проверка всех требований
    result['is_strong'] = all([
        result['length'] >= 8,
        result['has_digit'],
        result['has_lowercase'],
        result['has_uppercase'],
        result['has_special']
    ])
    
    # Оценка сложности
    score = 0
    if result['length'] >= 8:
        score += 1
    if result['length'] >= 12:
        score += 1
    if result['has_digit']:
        score += 1
    if result['has_lowercase']:
        score += 1
    if result['has_uppercase']:
        score += 1
    if result['has_special']:
        score += 1
    
    if score <= 2:
        result['strength'] = 'weak'
    elif score <= 4:
        result['strength'] = 'medium'
    else:
        result['strength'] = 'strong'
    
    return result