from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Notes API is working!"}

def test_create_note():
    r = client.post("/notes/", json={
        "title": "Test Note",
        "content": "Test Content",
        "tags": "test, api"
    })
    assert r.status_code == 200
    assert r.json()["title"] == "Test Note"

def test_search_notes():
    client.post("/notes/", json={"title": "Python", "content": "FastAPI"})
    r = client.get("/notes/?search=Python")
    assert r.status_code == 200
    assert len(r.json()) > 0

def test_filter_by_tag():
    r = client.get("/notes/?tag=python")
    assert r.status_code == 200