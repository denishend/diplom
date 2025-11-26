from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from enum import Enum

class SortOrder(str, Enum):
    created_asc = "created_at_asc"
    created_desc = "created_at_desc"
    title_asc = "title_asc"
    title_desc = "title_desc"

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/", response_model=schemas.NoteOut)
def create(data: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, data)


@router.get("/", response_model=list[schemas.NoteOut])
def list_notes(
    search: str | None = Query(None),
    tag: str | None = Query(None),
    sort: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return crud.get_notes_with_filters(
        db,
        search=search,
        tag=tag,
        sort=sort,
        skip=skip,
        limit=limit,
    )


@router.get("/{note_id}", response_model=schemas.NoteOut)
def get(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    return note


@router.put("/{note_id}", response_model=schemas.NoteOut)
def update(note_id: int, data: schemas.NoteUpdate, db: Session = Depends(get_db)):
    note = crud.update_note(db, note_id, data)
    if not note:
        raise HTTPException(404, "Note not found")
    return note


@router.delete("/{note_id}")
def delete(note_id: int, db: Session = Depends(get_db)):
    note = crud.delete_note(db, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    return {"deleted": True}
