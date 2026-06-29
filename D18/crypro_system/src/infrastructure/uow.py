# src/infrastructure/uow.py
"""
Unit of Work pattern
"""
from contextlib import contextmanager
from typing import Generator, Optional

from .repositories import PasswordRepository, TokenRepository, InMemoryRepository


class UnitOfWork:
    """Unit of Work для управления транзакциями"""
    
    def __init__(self):
        self._repositories = {}
        self._is_active = False
    
    def register_repository(self, name: str, repository: InMemoryRepository) -> None:
        """Регистрация репозитория"""
        self._repositories[name] = repository
    
    def get_repository(self, name: str) -> Optional[InMemoryRepository]:
        """Получение репозитория"""
        return self._repositories.get(name)
    
    def __enter__(self):
        self._is_active = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_active = False
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
    
    def commit(self) -> None:
        """Фиксация изменений"""
        if self._is_active:
            # В in-memory реализации ничего не делаем
            pass
    
    def rollback(self) -> None:
        """Откат изменений"""
        if self._is_active:
            # В in-memory реализации ничего не делаем
            pass


@contextmanager
def unit_of_work() -> Generator[UnitOfWork, None, None]:
    """Контекстный менеджер для Unit of Work"""
    uow = UnitOfWork()
    
    # Регистрируем репозитории
    uow.register_repository("password", PasswordRepository())
    uow.register_repository("token", TokenRepository())
    
    with uow:
        yield uow