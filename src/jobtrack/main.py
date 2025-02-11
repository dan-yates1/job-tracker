from datetime import timedelta
from typing import List, Optional
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .core.auth import get_current_user
from .core.supabase import init_supabase_schema
from .routes import auth, ai
from .schemas.job import Job, JobCreate, JobUpdate, JobInteraction, JobInteractionCreate
from .services.job import (
    create_job,
    get_user_jobs,
    get_job,
    update_job,
    delete_job,
    create_job_interaction,
    get_job_interactions
)

app = FastAPI(title="JobTrack AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/jobtrack/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="src/jobtrack/templates")

@app.on_event("startup")
async def startup_event():
    """Initialize database schema on startup"""
    init_supabase_schema()

# Include routers
app.include_router(auth.router)
app.include_router(ai.router)

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Job endpoints
@app.post("/jobs/", response_model=Job)
async def create_new_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new job entry."""
    return create_job(current_user.id, job)

@app.get("/jobs/", response_model=List[Job])
async def read_user_jobs(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all jobs for the current user."""
    return get_user_jobs(current_user.id)

@app.get("/jobs/{job_id}", response_model=Job)
async def read_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get a specific job by ID."""
    job = get_job(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.patch("/jobs/{job_id}", response_model=Job)
async def update_existing_job(
    job_id: UUID,
    job_update: JobUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a job entry."""
    job = update_job(job_id, current_user.id, job_update)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.delete("/jobs/{job_id}")
async def delete_existing_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete a job entry."""
    if not delete_job(job_id, current_user.id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@app.post("/jobs/{job_id}/interactions/", response_model=JobInteraction)
async def create_new_job_interaction(
    job_id: UUID,
    interaction: JobInteractionCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new interaction for a job."""
    # Verify job exists and belongs to user
    job = get_job(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return create_job_interaction(interaction)

@app.get("/jobs/{job_id}/interactions/", response_model=List[JobInteraction])
async def read_job_interactions(
    job_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all interactions for a job."""
    # Verify job exists and belongs to user
    job = get_job(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return get_job_interactions(job_id)
