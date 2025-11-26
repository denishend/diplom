from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# TODO: КРИТИЧНО! Hardcoded абсолютный путь Windows не работает на других ОС!
# Используйте относительный путь или переменные окружения
# См. REVIEW.md секция "Критические проблемы" пункт 1
# Правильно: DATABASE_URL = "sqlite:///./notes.db"
from app.config import settings

DATABASE_URL = settings.database_url


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
