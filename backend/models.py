from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""
    notes: str = ""
    expiry_date: Optional[date] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    notes: Optional[str] = None
    expiry_date: Optional[date] = None


class Todo(BaseModel):
    id: int
    title: str
    description: str
    notes: str
    expiry_date: Optional[date] = None

    class Config:
        from_attributes = True
