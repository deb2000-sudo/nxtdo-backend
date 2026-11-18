from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Optional
import logging

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lazy imports to avoid startup issues
@lru_cache
def get_settings():
    from app.core.config import settings
    return settings


def get_db_service():
    from app.core.database import db_service
    return db_service


def init_firebase():
    from app.core.firebase import get_firebase_app
    return get_firebase_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        settings = get_settings()
        init_firebase()
        logger.info(f"App started - Environment: {settings.ENVIRONMENT}")
    except Exception as e:
        logger.warning(f"Firebase init skipped: {e}")
    yield
    # Shutdown
    logger.info("App shutting down")


app = FastAPI(title="NxtDo API", lifespan=lifespan)


# Global handler: unexpected errors get logged, client sees a generic message.
# HTTPException (404, 400, etc.) is still handled by FastAPI as usual.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Task(TaskCreate):
    id: str


# Utility routes
@app.get("/")
def read_root():
    settings = get_settings()
    return {
        "message": "Hello from nxtdo-backend! I am Debashis Nayak",
        "environment": settings.ENVIRONMENT,
        "project": settings.GCP_PROJECT_ID,
    }


@app.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "firebase_project": settings.get_firebase_config()["project_id"],
    }


@app.get("/about", response_class=PlainTextResponse)
def about_backend():
    return "This is all backend"


# Task CRUD endpoints
@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    """Create a new task"""
    db = get_db_service()
    data = task.model_dump()
    task_id = db.create_document("tasks", data)
    return {"id": task_id, **data}


@app.get("/tasks")
def list_tasks(limit: int = Query(100, ge=1, le=500)):
    """List all tasks"""
    db = get_db_service()
    settings = get_settings()
    tasks = db.list_documents("tasks", limit=limit)
    return {
        "tasks": tasks,
        "count": len(tasks),
        "environment": settings.ENVIRONMENT,
    }


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    """Get a specific task"""
    db = get_db_service()
    task = db.get_document("tasks", task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    db = get_db_service()

    if not db.get_document("tasks", task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    # Only fields the client actually sent (allows setting a field to null)
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    db.update_document("tasks", task_id, update_data)
    return db.get_document("tasks", task_id)


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    """Delete a task"""
    db = get_db_service()

    if not db.get_document("tasks", task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete_document("tasks", task_id)
    return {"message": "Task deleted", "id": task_id}


# Legacy endpoints (remove if nothing uses them)
@app.get("/testing")
def test_endpoint():
    settings = get_settings()
    return {
        "message": "This is a Testing endpoint!",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/checking")
def check_endpoint():
    settings = get_settings()
    return {
        "message": "This is a Checking endpoint!",
        "environment": settings.ENVIRONMENT,
    }