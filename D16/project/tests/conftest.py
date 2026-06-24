import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Фикстура, создающая in-memory SQLite базу данных для каждого теста.
    После теста сессия закрывается и таблицы удаляются.
    """
    # Создаём in-memory SQLite
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Создаём все таблицы
    Base.metadata.create_all(engine)
    
    # Создаём сессию
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Удаляем таблицы после теста
        Base.metadata.drop_all(engine)