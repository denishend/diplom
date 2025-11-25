from datetime import datetime
from typing import Optional

from pydantic import BaseModel

# TODO: Добавьте валидацию с Field и validator
# Нет ограничений на длину, пустые значения
# См. REVIEW.md секция "Критические проблемы" пункт 3
class NoteBase(BaseModel):
    title: str  # TODO: добавить Field(..., min_length=1, max_length=200)
    content: str  # TODO: добавить Field(..., min_length=1)
    tags: Optional[str] = ""  # TODO: добавить Field(default="", max_length=200)

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None

class NoteOut(NoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True