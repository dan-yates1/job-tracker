from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, HttpUrl
from enum import Enum

class JobStatus(str, Enum):
    APPLIED = 'applied'
    INTERVIEWING = 'interviewing'
    OFFER_RECEIVED = 'offer_received'
    REJECTED = 'rejected'
    ACCEPTED = 'accepted'
    WITHDRAWN = 'withdrawn'

class RemoteType(str, Enum):
    ONSITE = 'on-site'
    HYBRID = 'hybrid'
    REMOTE = 'remote'

class JobInteractionType(str, Enum):
    INTERVIEW = 'interview'
    FOLLOW_UP = 'follow_up'
    OFFER = 'offer'
    REJECTION = 'rejection'
    OTHER = 'other'

class JobInteractionBase(BaseModel):
    interaction_type: JobInteractionType
    interaction_date: datetime
    notes: Optional[str] = None

class JobInteractionCreate(JobInteractionBase):
    job_id: UUID

class JobInteraction(JobInteractionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobBase(BaseModel):
    company_name: str
    position_title: str
    job_description: Optional[str] = None
    job_url: Optional[HttpUrl] = None
    status: JobStatus = JobStatus.APPLIED
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    remote_type: Optional[RemoteType] = None
    notes: Optional[str] = None
    applied_date: date = date.today()

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    interactions: List[JobInteraction] = []

    class Config:
        from_attributes = True

class JobUpdate(BaseModel):
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    job_description: Optional[str] = None
    job_url: Optional[HttpUrl] = None
    status: Optional[JobStatus] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    remote_type: Optional[RemoteType] = None
    notes: Optional[str] = None
    applied_date: Optional[date] = None

class CompanyBase(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class JobApplicationBase(BaseModel):
    position_title: str
    company_id: int
    status: str  # applied, interview, offer, rejected
    salary_range_min: Optional[float] = None
    salary_range_max: Optional[float] = None
    job_description: Optional[str] = None
    application_url: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplication(JobApplicationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    company: Company

    class Config:
        from_attributes = True

class InteractionBase(BaseModel):
    type: str  # email, phone, interview, offer
    notes: str
    date: datetime

class InteractionCreate(InteractionBase):
    job_application_id: int

class Interaction(InteractionBase):
    id: int
    job_application_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None  # e.g., programming, soft skills, tools
    description: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class JobApplicationWithDetails(JobApplication):
    interactions: List[Interaction] = []
    skills: List[Skill] = []
