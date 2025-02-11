from datetime import timedelta
from typing import List, Optional
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

from .config import settings
from .schemas.token import Token
from .schemas.user import User, UserCreate
from .schemas.job import Job, JobCreate, JobUpdate, JobInteraction, JobInteractionCreate
from .services.user import authenticate_user, create_user, get_user_by_email
from .services.job import (
    create_job,
    get_user_jobs,
    get_job,
    update_job,
    delete_job,
    create_job_interaction,
    get_job_interactions
)
from .core.security import create_access_token
from .core.auth import get_current_user
from .core.supabase import init_supabase_schema

app = FastAPI(title="JobTrack AI")

# Mount static files
app.mount("/static", StaticFiles(directory="src/jobtrack/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="src/jobtrack/templates")

@app.on_event("startup")
async def startup_event():
    """Initialize database schema on startup"""
    init_supabase_schema()

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

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=User)
async def create_new_user(user: UserCreate):
    db_user = get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return create_user(user=user)

# Job endpoints
@app.post("/jobs/", response_model=Job)
async def create_new_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new job entry."""
    return create_job(current_user.id, job)

@app.get("/jobs/", response_model=List[Job])
async def read_user_jobs(
    current_user: User = Depends(get_current_user)
):
    """Get all jobs for the current user."""
    return get_user_jobs(current_user.id)

@app.get("/jobs/{job_id}", response_model=Job)
async def read_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get a specific job by ID."""
    job = get_job(job_id, current_user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.put("/jobs/{job_id}", response_model=Job)
async def update_existing_job(
    job_id: UUID,
    job_update: JobUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a job entry."""
    updated_job = update_job(job_id, current_user.id, job_update)
    if updated_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@app.delete("/jobs/{job_id}")
async def delete_existing_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete a job entry."""
    success = delete_job(job_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job successfully deleted"}

@app.post("/jobs/{job_id}/interactions/", response_model=JobInteraction)
async def create_new_job_interaction(
    job_id: UUID,
    interaction: JobInteractionCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new interaction for a job."""
    # Verify the job exists and belongs to the user
    job = get_job(job_id, current_user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return create_job_interaction(interaction)

@app.get("/jobs/{job_id}/interactions/", response_model=List[JobInteraction])
async def read_job_interactions(
    job_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get all interactions for a job."""
    # Verify the job exists and belongs to the user
    job = get_job(job_id, current_user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return get_job_interactions(job_id)
