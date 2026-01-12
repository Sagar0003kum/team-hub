from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.workspace import MemberRole


class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspaceMemberBase(BaseModel):
    user_id: int
    role: MemberRole = MemberRole.MEMBER


class WorkspaceMemberCreate(WorkspaceMemberBase):
    pass


class WorkspaceMemberResponse(BaseModel):
    id: int
    user_id: int
    role: MemberRole
    joined_at: datetime
    user_email: Optional[str] = None
    user_display_name: Optional[str] = None

    class Config:
        from_attributes = True


class WorkspaceResponse(WorkspaceBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceDetailResponse(WorkspaceResponse):
    members: List[WorkspaceMemberResponse] = []
