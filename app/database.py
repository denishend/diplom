from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# TODO: КРИТИЧНО! Hardcoded абсолютный путь Windows не работает на других ОС!
# Используйте относительный путь или переменные окружения
# См. REVIEW.md секция "Критические проблемы" пункт 1
# Правильно: DATABASE_URL = "sqlite:///./notes.db"
DATABASE_URL = r"sqlite:///C:\Users\shend\PycharmProjects\DP\notes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()