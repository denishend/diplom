from typing import List
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging

from app.models import Note
from app.schemas import NoteCreate, NoteUpdate

logger = logging.getLogger(__name__)


def get_notes_with_filters(
    db: Session,
    search: str | None = None,
    tag: str | None = None,
    sort: str | None = None,
    skip: int = 0,
    limit: int = 100
) -> List[Note]:

    query = db.query(Note)


    if search:
        safe = search.replace('%', "\\%").replace('_', "\\_")
        pattern = f"%{safe}%"
        query = query.filter(
            (Note.title.ilike(pattern, escape='\\')) |
            (Note.content.ilike(pattern, escape='\\'))
        )

    if tag:
        tags = [t.strip() for t in tag.split(',') if t.strip()]
        if len(tags) == 1:
            query = query.filter(Note.tags.ilike(f"%{tags[0]}%"))
        else:
            query = query.filter(or_(*[Note.tags.ilike(f"%{t}%") for t in tags]))

    if sort == "created_at_asc":
        query = query.order_by(asc(Note.created_at))
    elif sort == "created_at_desc":
        query = query.order_by(desc(Note.created_at))
    elif sort == "title_asc":
        query = query.order_by(asc(Note.title))
    elif sort == "title_desc":
        query = query.order_by(desc(Note.title))
    else:
        query = query.order_by(desc(Note.created_at))

    return query.offset(skip).limit(limit).all()


def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()


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
        raise HTTPException(status_code=500, detail="Database error creating note")


def update_note(db: Session, note_id: int, note_data: NoteUpdate):
    note = get_note(db, note_id)
    if not note:
        return None

    for key, val in note_data.dict(exclude_unset=True).items():
        setattr(note, key, val)

    try:
        db.commit()
        db.refresh(note)
        return note
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating note {note_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error updating note")


def delete_note(db: Session, note_id: int):
    note = get_note(db, note_id)
    if not note:
        return False

    try:
        db.delete(note)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting note {note_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error deleting note")