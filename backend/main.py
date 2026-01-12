from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, users, workspaces, projects, tasks, comments, documents, dashboard
from app.core.config import settings
from app.db.database import engine, Base
from app.models import user, workspace, project, task, comment, document

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Hub API",
    description="A collaborative team workspace API",
    version="1.0.0"
)

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(workspaces.router, prefix="/api/workspaces", tags=["Workspaces"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
def root():
    return {"message": "Welcome to Team Hub API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}