from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.project import Project
from app.models.task import Task, TaskStatus, TaskPriority
from app.api.deps import get_current_user

router = APIRouter()


class TaskStats(BaseModel):
    total: int
    todo: int
    in_progress: int
    review: int
    done: int
    overdue: int


class PriorityStats(BaseModel):
    low: int
    medium: int
    high: int
    urgent: int


class WorkspaceStats(BaseModel):
    workspace_id: int
    workspace_name: str
    total_projects: int
    total_tasks: int
    task_stats: TaskStats
    priority_stats: PriorityStats
    recent_activity: List[dict]


class DashboardStats(BaseModel):
    total_workspaces: int
    total_projects: int
    total_tasks: int
    my_tasks: int
    overdue_tasks: int
    tasks_due_soon: int
    task_stats: TaskStats
    workspaces: List[WorkspaceStats]


def check_workspace_access(db: Session, workspace_id: int, user_id: int) -> bool:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return False
    
    if workspace.owner_id == user_id:
        return True
    
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    
    return member is not None


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get accessible workspaces
    owned_workspaces = db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()
    
    member_workspace_ids = db.query(WorkspaceMember.workspace_id).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()
    member_workspace_ids = [w[0] for w in member_workspace_ids]
    
    member_workspaces = db.query(Workspace).filter(
        Workspace.id.in_(member_workspace_ids)
    ).all() if member_workspace_ids else []
    
    all_workspaces = {w.id: w for w in owned_workspaces + member_workspaces}
    workspaces = list(all_workspaces.values())
    workspace_ids = list(all_workspaces.keys())
    
    # Get all projects
    projects = db.query(Project).filter(Project.workspace_id.in_(workspace_ids)).all()
    project_ids = [p.id for p in projects]
    
    # Get all tasks
    tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).all() if project_ids else []
    
    now = datetime.utcnow()
    soon = now + timedelta(days=7)
    
    # Calculate overall stats
    total_tasks = len(tasks)
    my_tasks = len([t for t in tasks if t.assignee_id == current_user.id])
    overdue_tasks = len([t for t in tasks if t.due_date and t.due_date < now and t.status != TaskStatus.DONE])
    tasks_due_soon = len([t for t in tasks if t.due_date and now <= t.due_date <= soon and t.status != TaskStatus.DONE])
    
    task_stats = TaskStats(
        total=total_tasks,
        todo=len([t for t in tasks if t.status == TaskStatus.TODO]),
        in_progress=len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
        review=len([t for t in tasks if t.status == TaskStatus.REVIEW]),
        done=len([t for t in tasks if t.status == TaskStatus.DONE]),
        overdue=overdue_tasks
    )
    
    # Per-workspace stats
    workspace_stats = []
    for workspace in workspaces:
        ws_projects = [p for p in projects if p.workspace_id == workspace.id]
        ws_project_ids = [p.id for p in ws_projects]
        ws_tasks = [t for t in tasks if t.project_id in ws_project_ids]
        
        ws_task_stats = TaskStats(
            total=len(ws_tasks),
            todo=len([t for t in ws_tasks if t.status == TaskStatus.TODO]),
            in_progress=len([t for t in ws_tasks if t.status == TaskStatus.IN_PROGRESS]),
            review=len([t for t in ws_tasks if t.status == TaskStatus.REVIEW]),
            done=len([t for t in ws_tasks if t.status == TaskStatus.DONE]),
            overdue=len([t for t in ws_tasks if t.due_date and t.due_date < now and t.status != TaskStatus.DONE])
        )
        
        priority_stats = PriorityStats(
            low=len([t for t in ws_tasks if t.priority == TaskPriority.LOW]),
            medium=len([t for t in ws_tasks if t.priority == TaskPriority.MEDIUM]),
            high=len([t for t in ws_tasks if t.priority == TaskPriority.HIGH]),
            urgent=len([t for t in ws_tasks if t.priority == TaskPriority.URGENT])
        )
        
        # Recent activity (last 5 tasks)
        recent_tasks = sorted(ws_tasks, key=lambda t: t.created_at, reverse=True)[:5]
        recent_activity = [
            {
                "task_id": t.id,
                "task_title": t.title,
                "status": t.status.value,
                "created_at": t.created_at.isoformat()
            }
            for t in recent_tasks
        ]
        
        workspace_stats.append(WorkspaceStats(
            workspace_id=workspace.id,
            workspace_name=workspace.name,
            total_projects=len(ws_projects),
            total_tasks=len(ws_tasks),
            task_stats=ws_task_stats,
            priority_stats=priority_stats,
            recent_activity=recent_activity
        ))
    
    return DashboardStats(
        total_workspaces=len(workspaces),
        total_projects=len(projects),
        total_tasks=total_tasks,
        my_tasks=my_tasks,
        overdue_tasks=overdue_tasks,
        tasks_due_soon=tasks_due_soon,
        task_stats=task_stats,
        workspaces=workspace_stats
    )


@router.get("/workspace/{workspace_id}/stats", response_model=WorkspaceStats)
def get_workspace_stats(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_workspace_access(db, workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workspace"
        )
    
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    projects = db.query(Project).filter(Project.workspace_id == workspace_id).all()
    project_ids = [p.id for p in projects]
    
    tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).all() if project_ids else []
    
    now = datetime.utcnow()
    
    task_stats = TaskStats(
        total=len(tasks),
        todo=len([t for t in tasks if t.status == TaskStatus.TODO]),
        in_progress=len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
        review=len([t for t in tasks if t.status == TaskStatus.REVIEW]),
        done=len([t for t in tasks if t.status == TaskStatus.DONE]),
        overdue=len([t for t in tasks if t.due_date and t.due_date < now and t.status != TaskStatus.DONE])
    )
    
    priority_stats = PriorityStats(
        low=len([t for t in tasks if t.priority == TaskPriority.LOW]),
        medium=len([t for t in tasks if t.priority == TaskPriority.MEDIUM]),
        high=len([t for t in tasks if t.priority == TaskPriority.HIGH]),
        urgent=len([t for t in tasks if t.priority == TaskPriority.URGENT])
    )
    
    recent_tasks = sorted(tasks, key=lambda t: t.created_at, reverse=True)[:10]
    recent_activity = [
        {
            "task_id": t.id,
            "task_title": t.title,
            "status": t.status.value,
            "created_at": t.created_at.isoformat()
        }
        for t in recent_tasks
    ]
    
    return WorkspaceStats(
        workspace_id=workspace.id,
        workspace_name=workspace.name,
        total_projects=len(projects),
        total_tasks=len(tasks),
        task_stats=task_stats,
        priority_stats=priority_stats,
        recent_activity=recent_activity
    )
