from typing import List

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models import Note
from app.schemas import NoteCreate, NoteUpdate


def get_notes_with_filters(db: Session, search: str | None = None, tag: str | None = None, sort: str | None = None) -> List[Note]:
    query = db.query(Note)

    # TODO: Добавьте экранирование спецсимволов для защиты от SQL LIKE injection
    # См. REVIEW.md секция "Критические проблемы" пункт 4
    if search:
        pattern = f"%{search}%"  # TODO: добавить search.replace('%', '\\%').replace('_', '\\_')
        query = query.filter(
            (Note.title.ilike(pattern)) | (Note.content.ilike(pattern))
        )

    if tag:
        tags = [t.strip() for t in tag.split(",") if t.strip()]
        if len(tags) == 1:
            query = query.filter(Note.tags.ilike(f"%{tags[0]}%"))
        else:
            from sqlalchemy import or_
            filters = [Note.tags.ilike(f"%{t}%") for t in tags]
            query = query.filter(or_(*filters))

    if sort:
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

    # TODO: Добавьте пагинацию (skip, limit)
    # При большом количестве заметок загружаются все
    # См. REVIEW.md секция "Критические проблемы" пункт 5
    return query.all()  # TODO: добавить .offset(skip).limit(limit)


def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

def create_note(db: Session, note: NoteCreate):
    # TODO: Добавьте обработку ошибок БД с try/except SQLAlchemyError
    # См. REVIEW.md секция "Критические проблемы" пункт 6
    n = Note(**note.dict())
    db.add(n)
    db.commit()
    db.refresh(n)
    return n

def update_note(db: Session, note_id: int, note_data: NoteUpdate):
    note = get_note(db, note_id)
    if not note:
        return None
    for key, val in note_data.dict(exclude_unset=True).items():
        setattr(note, key, val)
    db.commit()
    db.refresh(note)
    return note

def delete_note(db: Session, note_id: int):
    note = get_note(db, note_id)
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True
