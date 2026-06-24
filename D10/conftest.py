"""
Pytest конфигурация
"""
import pytest
import random

@pytest.fixture(autouse=True)
def reset_random_seed():
    """Сбрасываем seed для воспроизводимости"""
    random.seed(42)
    yield