from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

class CompanyBase(BaseModel):
    name: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class JobApplicationBase(BaseModel):
    job_title: str
    company_id: str
    job_description: Optional[str] = None
    job_url: Optional[HttpUrl] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    status: str = "applied"
    notes: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplication(JobApplicationBase):
    id: str
    user_id: str
    application_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class InteractionBase(BaseModel):
    job_application_id: str
    type: str
    date: datetime
    notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
