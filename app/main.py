import os

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .database import Base, engine
from .routers import notes

# TODO: Удалите эту строку! Используйте только Alembic миграции
# При каждом запуске пересоздаются таблицы, игнорируются миграции
# См. REVIEW.md секция "Критические проблемы" пункт 2
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API")

app.include_router(notes.router)

@app.get("/")
def root():
    return {"message": "Notes API is working!"}

@app.get("/app")
def frontend():
    return FileResponse(os.path.join(os.path.dirname(__file__), "templates", "index.html"))