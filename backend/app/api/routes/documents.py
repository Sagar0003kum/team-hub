from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.project import Project
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.api.deps import get_current_user

router = APIRouter()


def check_project_access(db: Session, project_id: int, user_id: int) -> bool:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    
    workspace = db.query(Workspace).filter(Workspace.id == project.workspace_id).first()
    if not workspace:
        return False
    
    if workspace.owner_id == user_id:
        return True
    
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace.id,
        WorkspaceMember.user_id == user_id
    ).first()
    
    return member is not None


@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_project_access(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project's documents"
        )
    
    documents = db.query(Document).filter(Document.project_id == project_id).order_by(Document.created_at.desc()).all()
    
    result = []
    for doc in documents:
        result.append(DocumentResponse(
            id=doc.id,
            project_id=doc.project_id,
            title=doc.title,
            content=doc.content,
            created_by=doc.created_by,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            creator_name=doc.created_by_user.display_name if doc.created_by_user else None
        ))
    
    return result


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_project_access(db, document_data.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create documents in this project"
        )
    
    document = Document(
        project_id=document_data.project_id,
        title=document_data.title,
        content=document_data.content,
        created_by=current_user.id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return DocumentResponse(
        id=document.id,
        project_id=document.project_id,
        title=document.title,
        content=document.content,
        created_by=document.created_by,
        created_at=document.created_at,
        updated_at=document.updated_at,
        creator_name=current_user.display_name
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not check_project_access(db, document.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this document"
        )
    
    return DocumentResponse(
        id=document.id,
        project_id=document.project_id,
        title=document.title,
        content=document.content,
        created_by=document.created_by,
        created_at=document.created_at,
        updated_at=document.updated_at,
        creator_name=document.created_by_user.display_name if document.created_by_user else None
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not check_project_access(db, document.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this document"
        )
    
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return DocumentResponse(
        id=document.id,
        project_id=document.project_id,
        title=document.title,
        content=document.content,
        created_by=document.created_by,
        created_at=document.created_at,
        updated_at=document.updated_at,
        creator_name=document.created_by_user.display_name if document.created_by_user else None
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not check_project_access(db, document.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this document"
        )
    
    db.delete(document)
    db.commit()
    return None
