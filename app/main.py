import os

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .database import Base, engine
from .routers import notes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API")

app.include_router(notes.router)

@app.get("/")
def root():
    return {"message": "Notes API is working!"}

@app.get("/app")
def frontend():
    return FileResponse(os.path.join(os.path.dirname(__file__), "templates", "index.html"))