from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy imports to avoid startup issues
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

app = FastAPI(
    title="NxtDo API",
    lifespan=lifespan
)

# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

@app.get("/")
def read_root():
    settings = get_settings()
    return {
        "message": "Hello from nxtdo-backend!",
        "environment": settings.ENVIRONMENT,
        "project": settings.GCP_PROJECT_ID
    }

@app.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "firebase_project": settings.get_firebase_config()["project_id"]
    }

# Task CRUD endpoints
@app.post("/task")
def create_task(task: TaskCreate):
    """Create a new task"""
    try:
        db = get_db_service()
        task_id = db.create_document("tasks", task.model_dump())
        return {"id": task_id, **task.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
def list_tasks(limit: int = 100):
    """List all tasks"""
    try:
        db = get_db_service()
        settings = get_settings()
        tasks = db.list_documents("tasks", limit=limit)
        return {
            "tasks": tasks,
            "count": len(tasks),
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    """Get a specific task"""
    try:
        db = get_db_service()
        task = db.get_document("tasks", task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tasks/{task_id}")
def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    try:
        db = get_db_service()
        
        # Check if exists
        existing = db.get_document("tasks", task_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update only provided fields
        update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
        db.update_document("tasks", task_id, update_data)
        
        return db.get_document("tasks", task_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    """Delete a task"""
    try:
        db = get_db_service()
        
        existing = db.get_document("tasks", task_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete_document("tasks", task_id)
        return {"message": "Task deleted", "id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoints
@app.get("/testing")
def test_endpoint():
    settings = get_settings()
    return {
        "message": "This is a Testing endpoint!",
        "environment": settings.ENVIRONMENT
    }

@app.get("/checking")
def check_endpoint():
    settings = get_settings()
    return {
        "message": "This is a Checking endpoint!",
        "environment": settings.ENVIRONMENT
    }