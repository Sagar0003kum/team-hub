from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    content: Optional[str] = None


class DocumentCreate(DocumentBase):
    project_id: int


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    project_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True
