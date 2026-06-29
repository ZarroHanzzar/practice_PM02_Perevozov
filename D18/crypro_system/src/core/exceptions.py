# src/core/exceptions.py
"""
Custom exceptions for cryptographic operations
"""

class CryptoError(Exception):
    """Базовое исключение для криптографических операций"""
    pass


class PasswordError(CryptoError):
    """Ошибка при работе с паролями"""
    pass


class TokenError(CryptoError):
    """Ошибка при работе с токенами"""
    pass


class EncryptionError(CryptoError):
    """Ошибка при шифровании/дешифровании"""
    pass


class HMACError(CryptoError):
    """Ошибка при работе с HMAC"""
    pass


class InvalidPasswordError(PasswordError):
    """Некорректный пароль"""
    pass


class ExpiredTokenError(TokenError):
    """Истекший токен"""
    pass


class InvalidSignatureError(TokenError):
    """Некорректная подпись"""
    pass