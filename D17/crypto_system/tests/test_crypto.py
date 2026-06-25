# tests/test_crypto.py

import pytest
import hashlib
from src.crypto import CryptoService


class TestCryptoService:

    @pytest.fixture
    def crypto(self):
        return CryptoService(
            "test_secret_key_32_bytes_long_12345"
        )

    @pytest.fixture
    def crypto_without_key(self):
        with pytest.raises(
            ValueError,
            match="Secret key must be at least 32 characters long"
        ):
            return CryptoService("short")

    # === Тесты для __init__ ===

    def test_init_with_valid_key(self):
        """Инициализация с валидным ключом."""
        crypto = CryptoService(
            "valid_secret_key_32_bytes_long_12345"
        )
        assert crypto.secret_key == "valid_secret_key_32_bytes_long_12345"

    def test_init_with_short_key(self):
        """Инициализация с коротким ключом выбрасывает исключение."""
        with pytest.raises(
            ValueError,
            match="Secret key must be at least 32 characters long"
        ):
            CryptoService("short")

    # === Тесты для hash_password ===

    def test_hash_password_basic(self, crypto):
        """Базовое хеширование пароля."""
        result = crypto.hash_password("my_password")
        assert 'hash' in result
        assert 'salt' in result
        assert result['algorithm'] == 'pbkdf2_sha256'
        assert len(result['hash']) == 64

    def test_hash_password_empty(self, crypto):
        """Пустой пароль выбрасывает исключение."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            crypto.hash_password("")

    def test_hash_password_unicode(self, crypto):
        """Unicode пароль."""
        password = "пароль_с_unicode_🌟"
        result = crypto.hash_password(password)
        assert 'hash' in result
        assert len(result['hash']) == 64

    def test_hash_password_same_password_different_salt(self, crypto):
        """Одинаковый пароль с разной солью дает разный хеш."""
        result1 = crypto.hash_password("password123")
        result2 = crypto.hash_password("password123")
        assert result1['hash'] != result2['hash']
        assert result1['salt'] != result2['salt']

    def test_hash_password_same_password_same_salt(self, crypto):
        """Одинаковый пароль с одинаковой солью дает одинаковый хеш."""
        salt = "fixed_salt_1234567890"
        result1 = crypto.hash_password("password123", salt)
        result2 = crypto.hash_password("password123", salt)
        assert result1['hash'] == result2['hash']

    @pytest.mark.parametrize("password", [
        " ",
        "123",
        "P@ssw0rd!",
        "a" * 1000,
        "пароль_с_unicode",
        "🌍🌎🌏"
    ])
    def test_hash_password_various_inputs(self, crypto, password):
        """Параметризованный тест для разных паролей."""
        result = crypto.hash_password(password)
        assert 'hash' in result
        assert 'salt' in result
        assert len(result['hash']) == 64

    # === Тесты для verify_password ===

    def test_verify_password_correct(self, crypto):
        """Проверка правильного пароля."""
        password = "correct_password"
        hashed = crypto.hash_password(password)
        assert crypto.verify_password(
            password,
            hashed['hash'],
            hashed['salt']
        ) is True

    def test_verify_password_incorrect(self, crypto):
        """Проверка неправильного пароля."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = crypto.hash_password(password)
        assert crypto.verify_password(
            wrong_password,
            hashed['hash'],
            hashed['salt']
        ) is False

    def test_verify_password_empty_parameters(self, crypto):
        """Проверка с пустыми параметрами."""
        assert crypto.verify_password("", "hash", "salt") is False
        assert crypto.verify_password("pass", "", "salt") is False
        assert crypto.verify_password("pass", "hash", "") is False

    def test_verify_password_unicode(self, crypto):
        """Проверка Unicode пароля."""
        password = "пароль_🌟"
        hashed = crypto.hash_password(password)
        assert crypto.verify_password(
            password,
            hashed['hash'],
            hashed['salt']
        ) is True

    # === Тесты для encrypt_data ===

    def test_encrypt_decrypt_data(self, crypto):
        """Шифрование и дешифрование данных."""
        original_data = {
            "user_id": 1,
            "email": "test@example.com",
            "data": "test_unicode_🌟"
        }
        encrypted = crypto.encrypt_data(original_data)
        decrypted = crypto.decrypt_data(encrypted)
        assert decrypted == original_data

    def test_encrypt_empty_data(self, crypto):
        """Шифрование пустых данных."""
        encrypted = crypto.encrypt_data({})
        decrypted = crypto.decrypt_data(encrypted)
        assert decrypted == {}

    def test_encrypt_nested_data(self, crypto):
        """Шифрование вложенных данных."""
        original_data = {
            "user": {
                "id": 1,
                "profile": {
                    "name": "John",
                    "settings": {"theme": "dark"}
                }
            }
        }
        encrypted = crypto.encrypt_data(original_data)
        decrypted = crypto.decrypt_data(encrypted)
        assert decrypted == original_data

    def test_encrypt_data_with_unicode(self, crypto):
        """Шифрование с Unicode символами."""
        original_data = {
            "text": "Привет мир! 🌍",
            "emoji": "🌟⭐🌈"
        }
        encrypted = crypto.encrypt_data(original_data)
        decrypted = crypto.decrypt_data(encrypted)
        assert decrypted == original_data

    def test_decrypt_invalid_data(self, crypto):
        """Дешифрование невалидных данных."""
        with pytest.raises(ValueError, match="Failed to decrypt data"):
            crypto.decrypt_data("invalid_base64_data")

    def test_decrypt_tampered_data(self, crypto):
        """Дешифрование измененных данных."""
        original_data = {"user_id": 1}
        encrypted = crypto.encrypt_data(original_data)
        # Изменяем данные
        tampered = encrypted[:-1] + "x"
        with pytest.raises(ValueError, match="Failed to decrypt data"):
            crypto.decrypt_data(tampered)

    # === Тесты для hash_string ===

    def test_hash_string_sha256(self, crypto):
        """Хеширование через SHA-256."""
        result = crypto.hash_string("test_string", "sha256")
        assert len(result) == 64

    def test_hash_string_sha1(self, crypto):
        """Хеширование через SHA-1."""
        result = crypto.hash_string("test_string", "sha1")
        assert len(result) == 40

    def test_hash_string_sha512(self, crypto):
        """Хеширование через SHA-512."""
        result = crypto.hash_string("test_string", "sha512")
        assert len(result) == 128

    def test_hash_string_md5(self, crypto):
        """Хеширование через MD5."""
        result = crypto.hash_string("test_string", "md5")
        assert len(result) == 32

    def test_hash_string_unsupported_algorithm(self, crypto):
        """Неподдерживаемый алгоритм выбрасывает исключение."""
        with pytest.raises(
            ValueError,
            match="Unsupported algorithm: unsupported"
        ):
            crypto.hash_string("test", "unsupported")

    def test_hash_string_unicode(self, crypto):
        """Хеширование Unicode строки."""
        result = crypto.hash_string("Привет мир! 🌍", "sha256")
        assert len(result) == 64

    @pytest.mark.parametrize("text, algorithm, expected_length", [
        ("Hello", "sha256", 64),
        ("Привет", "sha256", 64),
        ("", "sha256", 64),
        ("Hello", "sha1", 40),
        ("Hello", "md5", 32),
        ("", "sha1", 40),
    ])
    def test_hash_string_parametrized(
        self,
        crypto,
        text,
        algorithm,
        expected_length
    ):
        """Параметризованные тесты для hash_string."""
        result = crypto.hash_string(text, algorithm)
        assert isinstance(result, str)
        assert len(result) == expected_length

    # === Тесты для generate_api_key ===

    def test_generate_api_key(self, crypto):
        """Генерация API ключа."""
        key1 = crypto.generate_api_key(1)
        key2 = crypto.generate_api_key(1)
        assert key1 != key2
        assert key1.startswith("api_1_")
        assert len(key1) == len("api_1_") + 32

    def test_generate_api_key_different_users(self, crypto):
        """Генерация ключей для разных пользователей."""
        key1 = crypto.generate_api_key(1)
        key2 = crypto.generate_api_key(2)
        assert key1 != key2
        assert key1.startswith("api_1_")
        assert key2.startswith("api_2_")

    def test_generate_api_key_uniqueness(self, crypto):
        """Проверка уникальности ключей."""
        keys = {crypto.generate_api_key(i) for i in range(100)}
        assert len(keys) == 100

    def test_generate_api_key_format(self, crypto):
        """Проверка формата ключа."""
        key = crypto.generate_api_key(123)
        # Проверяем, что ключ начинается с правильного префикса
        assert key.startswith("api_123_")
        # Получаем случайную часть после префикса
        random_part = key[8:]  # "api_123_" это 8 символов
        # Проверяем длину случайной части (должна быть 32 символа)
        assert len(random_part) == 32
        # Проверяем, что все символы допустимы
        valid_chars = set(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
        )
        assert all(c in valid_chars for c in random_part)
        # Проверяем, что нет подчеркиваний в случайной части
        assert "_" not in random_part
        # Проверяем через split
        parts = key.split("_")
        assert len(parts) == 3
        assert parts[0] == "api"
        assert parts[1] == "123"
        assert len(parts[2]) == 32

    # === Тесты для secure_compare ===

    def test_secure_compare_equal(self, crypto):
        """Сравнение равных строк."""
        assert crypto.secure_compare("test", "test") is True

    def test_secure_compare_not_equal(self, crypto):
        """Сравнение разных строк."""
        assert crypto.secure_compare("test1", "test2") is False

    def test_secure_compare_empty_strings(self, crypto):
        """Сравнение пустых строк."""
        assert crypto.secure_compare("", "") is True
        assert crypto.secure_compare("", "test") is False

    def test_secure_compare_different_lengths(self, crypto):
        """Сравнение строк разной длины."""
        assert crypto.secure_compare("test", "test123") is False

    def test_secure_compare_unicode(self, crypto):
        """Сравнение Unicode строк."""
        assert crypto.secure_compare("Привет", "Привет") is True
        assert crypto.secure_compare("Привет", "Пока") is False

    # === Тесты для hash_file ===

    def test_hash_file_basic(self, crypto):
        """Хеширование файла."""
        content = b"test file content"
        result = crypto.hash_file(content)
        assert len(result) == 64
        assert crypto.hash_file(b"test file content") == result

    def test_hash_file_empty(self, crypto):
        """Хеширование пустого файла."""
        result = crypto.hash_file(b"")
        assert len(result) == 64
        assert result == hashlib.sha256(b"").hexdigest()

    def test_hash_file_different_content(self, crypto):
        """Разное содержимое дает разные хеши."""
        hash1 = crypto.hash_file(b"content1")
        hash2 = crypto.hash_file(b"content2")
        assert hash1 != hash2

    def test_hash_file_large_content(self, crypto):
        """Хеширование большого файла."""
        large_content = b"x" * 1000000
        result = crypto.hash_file(large_content)
        assert len(result) == 64

    # === Тесты для hash_with_unicode ===

    def test_hash_with_unicode_basic(self, crypto):
        """Хеширование с Unicode."""
        result = crypto.hash_with_unicode("Привет мир! 🌍")
        assert len(result) == 64

    def test_hash_with_unicode_empty(self, crypto):
        """Хеширование пустой строки."""
        result = crypto.hash_with_unicode("")
        assert len(result) == 64
        assert result == hashlib.sha256(b"").hexdigest()

    @pytest.mark.parametrize("text", [
        "Hello",
        "Привет",
        "🌍🌎🌏",
        "Hello 🌍",
        "Hello\tWorld\n",
        "a" * 1000,
    ])
    def test_hash_with_unicode_parametrized(self, crypto, text):
        """Параметризованные тесты для Unicode хеширования."""
        result = crypto.hash_with_unicode(text)
        assert len(result) == 64

    # === Тесты на все кодировки ===

    @pytest.mark.parametrize("text", [
        "Hello",  # ASCII
        "Привет",  # Кириллица
        "你好",  # Китайский
        "こんにちは",  # Японский
        "안녕하세요",  # Корейский
        "مرحبا",  # Арабский
        "שלום",  # Иврит
        "🌍🌎🌏",  # Эмодзи
        "Hello Привет 你好 こんにちは",  # Смешанные
    ])
    def test_unicode_encoding(self, crypto, text):
        """Тестирование разных кодировок."""
        hash_result = crypto.hash_string(text, "sha256")
        assert len(hash_result) == 64

        data = {"text": text}
        encrypted = crypto.encrypt_data(data)
        decrypted = crypto.decrypt_data(encrypted)
        assert decrypted == data

        file_hash = crypto.hash_file(text.encode('utf-8'))
        assert len(file_hash) == 64
