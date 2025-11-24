from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NoteBase(BaseModel):
    title: str
    content: str
    tags: Optional[str] = ""

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