# 📋 Code Review: Notes API

**Оценка:** 7/10  
**Дата:** 25 ноября 2025

---

## ✅ Сильные стороны

1. **Чистая архитектура** - отличное разделение на модули (models, schemas, crud, routers)
2. **Современный FastAPI** - правильное использование роутеров, зависимостей
3. **SQLAlchemy 2.0** - современная версия ORM
4. **Alembic миграции** - правильный подход к работе с БД
5. **Тесты** - есть базовое тестирование
6. **Функциональность** - полный CRUD + фильтры, поиск, сортировка

---

## 🔴 Критические проблемы (TODO - исправить)

### 1. **КРИТИЧНО: Hardcoded абсолютный путь Windows**
**Файл:** `app/database.py`, строка 4

```python
DATABASE_URL = r"sqlite:///C:\Users\shend\PycharmProjects\DP\notes.db"
```

❌ **Проблема:** 
- Не работает на других компьютерах и в Linux/Mac
- Раскрывает username системы (shend)
- Невозможно задеплоить

✅ **Исправление:**
```python
# app/database.py
import os
from pathlib import Path

# Используем относительный путь
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/notes.db"

# Или для production с переменными окружения:
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/notes.db")
```

Создайте `.env`:
```bash
DATABASE_URL=sqlite:///./notes.db
# Для PostgreSQL в production:
# DATABASE_URL=postgresql://user:password@localhost/notes_db
```

---

### 2. **TODO: Устаревшее создание таблиц**
**Файл:** `app/main.py`, строка 8

```python
Base.metadata.create_all(bind=engine)
```

❌ **Проблема:** Таблицы создаются при каждом запуске, игнорируются миграции Alembic.

✅ **Решение:** Удалите эту строку и используйте только Alembic:
```bash
# Создание миграции
alembic revision --autogenerate -m "Initial tables"

# Применение
alembic upgrade head
```

---

### 3. **TODO: Отсутствует валидация входных данных**
**Файл:** `app/schemas.py`

❌ **Проблема:** Нет ограничений на длину, пустые значения.

✅ **Исправление:**
```python
from pydantic import BaseModel, Field, validator

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: Optional[str] = Field(default="", max_length=200)
    
    @validator('title', 'content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Проверка формата тегов (через запятую)
            tags = [t.strip() for t in v.split(',')]
            if any(len(t) > 50 for t in tags):
                raise ValueError('Tag too long (max 50 chars)')
        return v
```

---

### 4. **TODO: SQL Injection риск в поиске**
**Файл:** `app/crud.py`, строка 16

```python
query = query.filter(
    (Note.title.ilike(pattern)) | (Note.content.ilike(pattern))
)
```

Хотя SQLAlchemy защищает, добавьте санитизацию:

```python
def get_notes_with_filters(db: Session, search: str | None = None, ...):
    query = db.query(Note)
    
    if search:
        # Экранируем спецсимволы SQL LIKE
        search = search.replace('%', '\\%').replace('_', '\\_')
        pattern = f"%{search}%"
        query = query.filter(
            (Note.title.ilike(pattern, escape='\\')) | 
            (Note.content.ilike(pattern, escape='\\'))
        )
```

---

### 5. **TODO: Отсутствует пагинация**
**Файл:** `app/routers/notes.py`, `app/crud.py`

❌ **Проблема:** При большом количестве записей загружаются все.

✅ **Исправление:**
```python
# app/routers/notes.py
@router.get("/", response_model=list[schemas.NoteOut])
def list_notes(
    search: str | None = None,
    tag: str | None = None,
    sort: str | None = None,
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=1000, description="Limit"),
    db: Session = Depends(get_db)
):
    notes = crud.get_notes_with_filters(
        db, search=search, tag=tag, sort=sort, 
        skip=skip, limit=limit
    )
    total = crud.get_notes_count(db, search=search, tag=tag)
    
    return {
        "items": notes,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# app/crud.py
def get_notes_with_filters(
    db: Session, 
    search: str | None = None, 
    tag: str | None = None, 
    sort: str | None = None,
    skip: int = 0,
    limit: int = 100
) -> List[Note]:
    query = db.query(Note)
    # ... фильтры ...
    return query.offset(skip).limit(limit).all()

def get_notes_count(db: Session, search: str | None = None, tag: str | None = None) -> int:
    query = db.query(Note)
    # ... те же фильтры ...
    return query.count()
```

---

### 6. **TODO: Нет обработки ошибок БД**
**Файл:** `app/crud.py`

Добавьте обработку:
```python
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def create_note(db: Session, note: NoteCreate):
    try:
        n = Note(**note.dict())
        db.add(n)
        db.commit()
        db.refresh(n)
        return n
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating note: {e}")
        raise HTTPException(500, "Database error")
```

---

### 7. **TODO: Отсутствует конфигурационный файл**

Создайте `app/config.py`:
```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str = "sqlite:///./notes.db"
    app_title: str = "Notes API"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

И используйте в `database.py`:
```python
from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
```

---

## 💡 Рекомендации (желательно)

### 1. Добавьте CORS для frontend
```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Добавьте логирование
```python
# app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. Расширьте тесты
```python
# tests/test_notes.py
def test_create_note():
    r = client.post("/notes/", json={
        "title": "Test Note",
        "content": "Test Content",
        "tags": "test, api"
    })
    assert r.status_code == 200
    assert r.json()["title"] == "Test Note"

def test_search_notes():
    # Создаём заметку
    client.post("/notes/", json={"title": "Python", "content": "FastAPI"})
    
    # Ищем
    r = client.get("/notes/?search=Python")
    assert r.status_code == 200
    assert len(r.json()) > 0

def test_filter_by_tag():
    r = client.get("/notes/?tag=python")
    assert r.status_code == 200
```

### 4. Добавьте README.md
```markdown
# Notes API

Простое REST API для управления заметками.

## Установка
\`\`\`bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
\`\`\`

## API Endpoints
- POST /notes/ - Создать заметку
- GET /notes/ - Список заметок (поиск, фильтры)
- GET /notes/{id} - Получить заметку
- PUT /notes/{id} - Обновить заметку
- DELETE /notes/{id} - Удалить заметку
```

### 5. Добавьте .gitignore
```
__pycache__/
*.py[cod]
*.db
*.sqlite
.env
.venv
venv/
.idea/
.vscode/
notes.db
```

### 6. Используйте enum для сортировки
```python
from enum import Enum

class SortOrder(str, Enum):
    created_asc = "created_at_asc"
    created_desc = "created_at_desc"
    title_asc = "title_asc"
    title_desc = "title_desc"

@router.get("/")
def list_notes(
    sort: SortOrder | None = None,
    ...
):
```

### 7. Добавьте метаданные для Swagger
```python
# app/main.py
app = FastAPI(
    title="Notes API",
    description="API для управления заметками с поиском и тегами",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

---

## 📊 Оценка

| Критерий | Балл | Комментарий |
|----------|------|-------------|
| Архитектура | 9/10 | Отличная структура |
| Функциональность | 8/10 | Полный CRUD + фильтры |
| Код качество | 7/10 | Чистый, но нет валидации |
| Безопасность | 6/10 | Hardcoded пути, нет валидации |
| Тестирование | 5/10 | Минимальные тесты |
| Документация | 4/10 | Нет README |

**Общая оценка: 7/10**

---

## 🎯 План исправлений

### Высокий приоритет (30 минут):
1. ✅ Исправить hardcoded путь в `database.py`
2. ✅ Удалить `Base.metadata.create_all()` из `main.py`
3. ✅ Добавить валидацию в `schemas.py`
4. ✅ Создать `config.py` и `.env`

### Средний приоритет (1 час):
5. Добавить пагинацию
6. Добавить обработку ошибок БД
7. Добавить логирование
8. Создать README.md

### Низкий приоритет (опционально):
9. Расширить тесты
10. Добавить CORS
11. Использовать Enum

---

## 🚀 Быстрые команды

```bash
# 1. Создайте .env
cat > .env << EOF
DATABASE_URL=sqlite:///./notes.db
APP_TITLE=Notes API
DEBUG=True
EOF

# 2. Установите pydantic-settings
pip install pydantic-settings

# 3. Примените миграции
alembic upgrade head

# 4. Запустите
uvicorn app.main:app --reload
```

---

## 💬 Заключение

Хороший, чистый проект с правильной архитектурой! Главная проблема - **hardcoded путь к БД**, который делает проект неработоспособным на других системах. После исправления критических моментов проект будет готов к использованию.

Отличная работа с SQLAlchemy, правильное использование Alembic, хорошая структура кода. Продолжай в том же духе! 🎉

---

**Ревьюер:** GitHub Copilot
