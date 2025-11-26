import os
from fastapi import FastAPI
from fastapi.responses import FileResponse

from .routers import notes
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notes API",
    description="API для управления заметками: создание, поиск, фильтры, сортировка",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(notes.router)


@app.get("/")
def root():
    return {"message": "Notes API is working!"}


@app.get("/app")
def frontend():
    return FileResponse(os.path.join(os.path.dirname(__file__), "templates", "index.html"))
