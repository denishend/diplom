from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: Optional[str] = Field("", max_length=200)

    @validator("title", "content")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Проверка формата тегов (через запятую)
            tags = [t.strip() for t in v.split(',')]
            if any(len(t) > 50 for t in tags):
                raise ValueError('Tag too long (max 50 chars)')
        return v

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[str] = Field(None, max_length=200)

class NoteOut(NoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True