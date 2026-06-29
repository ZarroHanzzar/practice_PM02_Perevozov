# tests/unit/test_uow.py
"""
Unit tests for Unit of Work
"""
import pytest
from src.infrastructure.uow import UnitOfWork, unit_of_work
from src.infrastructure.repositories import InMemoryRepository, PasswordRepository, TokenRepository


class TestUnitOfWork:
    """Тесты для UnitOfWork"""
    
    def test_create_uow(self):
        """Тест создания UnitOfWork"""
        uow = UnitOfWork()
        assert uow._is_active is False
        assert len(uow._repositories) == 0
    
    def test_register_repository(self):
        """Тест регистрации репозитория"""
        uow = UnitOfWork()
        repo = InMemoryRepository()
        uow.register_repository("test", repo)
        assert uow.get_repository("test") == repo
    
    def test_get_repository(self):
        """Тест получения репозитория"""
        uow = UnitOfWork()
        repo = InMemoryRepository()
        uow.register_repository("test", repo)
        assert uow.get_repository("test") == repo
    
    def test_get_nonexistent_repository(self):
        """Тест получения несуществующего репозитория"""
        uow = UnitOfWork()
        assert uow.get_repository("nonexistent") is None
    
    def test_context_manager_enter(self):
        """Тест входа в контекстный менеджер"""
        with UnitOfWork() as uow:
            assert uow._is_active is True
        assert uow._is_active is False
    
    def test_context_manager_exit_no_exception(self):
        """Тест выхода из контекстного менеджера без исключения"""
        uow = UnitOfWork()
        with uow:
            pass
        assert uow._is_active is False
    
    def test_commit(self):
        """Тест commit"""
        uow = UnitOfWork()
        uow._is_active = True
        uow.commit()
        # В in-memory реализации commit ничего не делает
        assert uow._is_active is True
    
    def test_rollback(self):
        """Тест rollback"""
        uow = UnitOfWork()
        uow._is_active = True
        uow.rollback()
        # В in-memory реализации rollback ничего не делает
        assert uow._is_active is True


class TestUnitOfWorkContextManager:
    """Тесты для контекстного менеджера UoW"""
    
    def test_unit_of_work_context(self):
        """Тест контекстного менеджера unit_of_work"""
        with unit_of_work() as uow:
            assert uow.get_repository("password") is not None
            assert uow.get_repository("token") is not None
    
    def test_uow_repositories_registered(self):
        """Тест регистрации репозиториев в UoW"""
        with unit_of_work() as uow:
            password_repo = uow.get_repository("password")
            token_repo = uow.get_repository("token")
            assert password_repo is not None
            assert token_repo is not None
            assert isinstance(password_repo, PasswordRepository)
            assert isinstance(token_repo, TokenRepository)
            assert password_repo != token_repo
    
    def test_uow_multiple_contexts(self):
        """Тест множественных контекстов UoW"""
        with unit_of_work() as uow1:
            with unit_of_work() as uow2:
                assert uow1 != uow2
                assert uow1.get_repository("password") != uow2.get_repository("password")