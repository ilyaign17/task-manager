from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# Используем SQLite: файл tasks.sqlite3 будет создан в корне проекта.
DATABASE_URL = "sqlite:///./tasks.sqlite3"

# Для SQLite в dev-режиме нужен флаг check_same_thread=False,
# иначе uvicorn будет ругаться на доступ из разных потоков.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,   # современный стиль SQLAlchemy 2.x
)

# Фабрика сессий. autocommit=False — явный контроль транзакций.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Базовый класс для декларативных моделей SQLAlchemy."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость FastAPI для получения сессии на время запроса.

    FastAPI сам вызовет .close() после выхода из yield.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
