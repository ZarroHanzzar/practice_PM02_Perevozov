# tests/unit/test_logger.py
"""
Unit tests for logger
"""
import pytest
import logging
import os
import time
from src.utils.logger import Logger, get_logger


class TestLogger:
    """Тесты для Logger"""
    
    def test_logger_singleton(self):
        """Тест singleton паттерна"""
        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2
    
    def test_get_logger(self):
        """Тест функции get_logger"""
        logger = get_logger()
        assert isinstance(logger, Logger)
    
    def test_logger_level(self):
        """Тест уровня логирования"""
        logger = Logger()
        assert logger.logger.level == logging.DEBUG
    
    def test_logger_handlers(self):
        """Тест наличия хендлеров"""
        logger = Logger()
        assert len(logger.logger.handlers) >= 2  # console + file
    
    def test_debug_log(self, caplog):
        """Тест debug логирования"""
        logger = Logger()
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            assert "Debug message" in caplog.text
    
    def test_info_log(self, caplog):
        """Тест info логирования"""
        logger = Logger()
        with caplog.at_level(logging.INFO):
            logger.info("Info message")
            assert "Info message" in caplog.text
    
    def test_warning_log(self, caplog):
        """Тест warning логирования"""
        logger = Logger()
        with caplog.at_level(logging.WARNING):
            logger.warning("Warning message")
            assert "Warning message" in caplog.text
    
    def test_error_log(self, caplog):
        """Тест error логирования"""
        logger = Logger()
        with caplog.at_level(logging.ERROR):
            logger.error("Error message")
            assert "Error message" in caplog.text
    
    def test_critical_log(self, caplog):
        """Тест critical логирования"""
        logger = Logger()
        with caplog.at_level(logging.CRITICAL):
            logger.critical("Critical message")
            assert "Critical message" in caplog.text
    
    def test_logger_file_exists(self):
        """Тест существования файла лога"""
        logger = Logger()
        # Проверяем, что файл лога существует
        assert os.path.exists('crypto_system.log')