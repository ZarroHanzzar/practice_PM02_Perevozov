# tests/unit/test_cli.py
"""
Unit tests for CLI
"""
import pytest
import json
import sys
from io import StringIO
from src.presentation.cli import CryptoCLI


class TestCryptoCLI:
    """Тесты для CryptoCLI"""
    
    def setup_method(self):
        self.cli = CryptoCLI()
    
    def test_cli_initialization(self):
        """Тест инициализации CLI"""
        assert self.cli.password_service is not None
        assert self.cli.token_service is not None
        assert self.cli.encryption_service is not None
        assert self.cli.hmac_service is not None
    
    def test_hash_command(self, capsys):
        """Тест команды hash"""
        self.cli.run(["hash", "my_password"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert 'hash' in result
        assert 'salt' in result
        assert result.get('algorithm') == 'sha256'
    
    def test_hash_command_with_salt(self, capsys):
        """Тест команды hash с солью"""
        self.cli.run(["hash", "my_password", "--salt", "fixed_salt"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result['salt'] == 'fixed_salt'
    
    def test_verify_command_correct(self, capsys):
        """Тест команды verify с правильным паролем"""
        # Сначала хешируем
        self.cli.run(["hash", "my_password"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        
        # Проверяем
        self.cli.run(["verify", "my_password", result['hash'], result['salt']])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result['is_valid'] is True
    
    def test_verify_command_incorrect(self, capsys):
        """Тест команды verify с неправильным паролем"""
        self.cli.run(["verify", "wrong", "fake_hash", "fake_salt"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result['is_valid'] is False
    
    def test_token_command(self, capsys):
        """Тест команды token"""
        self.cli.run(["token", "123", "secret"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert 'token' in result
        assert len(result['token']) > 0
    
    def test_token_command_with_expiry(self, capsys):
        """Тест команды token с временем жизни"""
        self.cli.run(["token", "123", "secret", "--expires", "48"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert 'token' in result
    
    def test_verify_token_command_valid(self, capsys):
        """Тест команды verify-token с валидным токеном"""
        # Генерируем токен
        self.cli.run(["token", "123", "secret"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        token = result['token']
        
        # Проверяем
        self.cli.run(["verify-token", token, "secret"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result['is_valid'] is True
        assert result['user_id'] == 123
    
    def test_verify_token_command_invalid(self, capsys):
        """Тест команды verify-token с невалидным токеном"""
        self.cli.run(["verify-token", "invalid_token", "secret"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result['is_valid'] is False
    
    def test_encrypt_command(self, capsys):
        """Тест команды encrypt"""
        self.cli.run(["encrypt", "Hello, World!", "key"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert 'encrypted' in result
        assert len(result['encrypted']) > 0
    
    def test_decrypt_command(self, capsys):
        """Тест команды decrypt"""
        # Сначала шифруем
        self.cli.run(["encrypt", "Hello, World!", "key"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        encrypted = result['encrypted']
        
        # Дешифруем
        self.cli.run(["decrypt", encrypted, "key"])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result['decrypted'] == "Hello, World!"
    
    def test_no_command(self, capsys):
        """Тест без команды"""
        self.cli.run([])
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "help" in captured.out.lower()
    
    def test_unknown_command(self, capsys):
        """Тест с неизвестной командой"""
        with pytest.raises(SystemExit):
            self.cli.run(["unknown_command"])