# tests/conftest.py
import pytest


@pytest.fixture
def sample_data():
    """Фикстура для генерации тестовых данных (10_000 записей)."""
    return [{"id": i, "value": i * 10} for i in range(10000)]


@pytest.fixture
def sample_data_small():
    """Фикстура для небольшого набора данных (100 записей)."""
    return [{"id": i, "value": i * 10} for i in range(100)]