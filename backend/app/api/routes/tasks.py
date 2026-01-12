from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskPositionUpdate
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


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if project_id:
        if not check_project_access(db, project_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
        tasks = db.query(Task).filter(Task.project_id == project_id).order_by(Task.position).all()
    else:
        # Get all tasks from accessible projects
        owned_workspaces = db.query(Workspace.id).filter(
            Workspace.owner_id == current_user.id
        ).all()
        
        member_workspaces = db.query(WorkspaceMember.workspace_id).filter(
            WorkspaceMember.user_id == current_user.id
        ).all()
        
        workspace_ids = [w[0] for w in owned_workspaces + member_workspaces]
        
        project_ids = db.query(Project.id).filter(
            Project.workspace_id.in_(workspace_ids)
        ).all()
        project_ids = [p[0] for p in project_ids]
        
        tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).order_by(Task.position).all()
    
    # Add assignee and creator names
    result = []
    for task in tasks:
        task_dict = TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            project_id=task.project_id,
            assignee_id=task.assignee_id,
            created_by=task.created_by,
            position=task.position,
            created_at=task.created_at,
            assignee_name=task.assignee.display_name if task.assignee else None,
            creator_name=task.creator.display_name if task.creator else None
        )
        result.append(task_dict)
    
    return result


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_project_access(db, task_data.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks in this project"
        )
    
    # Get max position for the status
    max_position = db.query(func.max(Task.position)).filter(
        Task.project_id == task_data.project_id,
        Task.status == task_data.status
    ).scalar() or 0
    
    task = Task(
        **task_data.model_dump(),
        created_by=current_user.id,
        position=max_position + 1
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        created_by=task.created_by,
        position=task.position,
        created_at=task.created_at,
        assignee_name=task.assignee.display_name if task.assignee else None,
        creator_name=current_user.display_name
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not check_project_access(db, task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        created_by=task.created_by,
        position=task.position,
        created_at=task.created_at,
        assignee_name=task.assignee.display_name if task.assignee else None,
        creator_name=task.creator.display_name if task.creator else None
    )


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not check_project_access(db, task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        created_by=task.created_by,
        position=task.position,
        created_at=task.created_at,
        assignee_name=task.assignee.display_name if task.assignee else None,
        creator_name=task.creator.display_name if task.creator else None
    )


@router.patch("/{task_id}/position", response_model=TaskResponse)
def update_task_position(
    task_id: int,
    position_update: TaskPositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task status and position (for drag-and-drop)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not check_project_access(db, task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    task.status = position_update.status
    task.position = position_update.position
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        created_by=task.created_by,
        position=task.position,
        created_at=task.created_at,
        assignee_name=task.assignee.display_name if task.assignee else None,
        creator_name=task.creator.display_name if task.creator else None
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not check_project_access(db, task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    db.delete(task)
    db.commit()
    return None
