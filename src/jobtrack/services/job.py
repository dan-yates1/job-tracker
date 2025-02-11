from datetime import datetime
from typing import List, Optional
from uuid import UUID
from ..core.supabase import supabase_client, get_supabase
from ..schemas.job import (
    CompanyCreate,
    Company,
    JobApplicationCreate,
    JobApplication,
    InteractionCreate,
    Interaction,
    SkillCreate,
    Skill,
    JobApplicationWithDetails,
    JobCreate, 
    JobUpdate, 
    JobInteractionCreate
)

class JobService:
    def create_company(self, company: CompanyCreate) -> Company:
        data = {
            **company.model_dump(),
            'created_at': datetime.utcnow().isoformat()
        }
        result = supabase_client.table('companies').insert(data).execute()
        return Company(**result.data[0])

    def create_job_application(self, application: JobApplicationCreate, user_id: int) -> JobApplication:
        data = {
            **application.model_dump(),
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        result = supabase_client.table('job_applications').insert(data).execute()
        return JobApplication(**result.data[0])

    def get_user_applications(self, user_id: int) -> List[JobApplicationWithDetails]:
        result = (supabase_client
                 .table('job_applications')
                 .select('*, company:companies(*), interactions(*), skills(*)')
                 .eq('user_id', user_id)
                 .order('created_at', desc=True)
                 .execute())
        return [JobApplicationWithDetails(**app) for app in result.data]

    def create_interaction(self, interaction: InteractionCreate) -> Interaction:
        data = {
            **interaction.model_dump(),
            'created_at': datetime.utcnow().isoformat()
        }
        result = supabase_client.table('interactions').insert(data).execute()
        return Interaction(**result.data[0])

    def get_application_interactions(self, application_id: int) -> List[Interaction]:
        result = (supabase_client
                 .table('interactions')
                 .select('*')
                 .eq('job_application_id', application_id)
                 .order('date', desc=True)
                 .execute())
        return [Interaction(**interaction) for interaction in result.data]

    def create_skill(self, skill: SkillCreate) -> Skill:
        data = {
            **skill.model_dump(),
            'created_at': datetime.utcnow().isoformat()
        }
        result = supabase_client.table('skills').insert(data).execute()
        return Skill(**result.data[0])

    def add_skills_to_application(self, application_id: int, skill_ids: List[int]) -> None:
        data = [
            {'job_application_id': application_id, 'skill_id': skill_id}
            for skill_id in skill_ids
        ]
        supabase_client.table('job_application_skills').insert(data).execute()

    def update_application_status(self, application_id: int, status: str) -> JobApplication:
        data = {
            'status': status,
            'updated_at': datetime.utcnow().isoformat()
        }
        result = (supabase_client
                 .table('job_applications')
                 .update(data)
                 .eq('id', application_id)
                 .execute())
        return JobApplication(**result.data[0])

    def get_application_stats(self, user_id: int) -> dict:
        applications = (supabase_client
                       .table('job_applications')
                       .select('status')
                       .eq('user_id', user_id)
                       .execute())
        
        stats = {
            'total': len(applications.data),
            'applied': 0,
            'interview': 0,
            'offer': 0,
            'rejected': 0
        }
        
        for app in applications.data:
            stats[app['status']] += 1
            
        return stats

def create_job(user_id: UUID, job: JobCreate) -> dict:
    """Create a new job entry."""
    client = get_supabase(use_service_key=True)
    
    job_data = job.model_dump()
    job_data['user_id'] = str(user_id)
    job_data['created_at'] = datetime.utcnow().isoformat()
    job_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = client.table('jobs').insert(job_data).execute()
    return result.data[0]

def get_user_jobs(user_id: UUID) -> List[dict]:
    """Get all jobs for a user."""
    client = get_supabase(use_service_key=True)
    result = (
        client.table('jobs')
        .select('*, job_interactions(*)')
        .eq('user_id', str(user_id))
        .order('created_at', desc=True)
        .execute()
    )
    return result.data

def get_job(job_id: UUID, user_id: UUID) -> Optional[dict]:
    """Get a specific job by ID."""
    client = get_supabase(use_service_key=True)
    result = (
        client.table('jobs')
        .select('*, job_interactions(*)')
        .eq('id', str(job_id))
        .eq('user_id', str(user_id))
        .execute()
    )
    return result.data[0] if result.data else None

def update_job(job_id: UUID, user_id: UUID, job_update: JobUpdate) -> Optional[dict]:
    """Update a job entry."""
    client = get_supabase(use_service_key=True)
    
    # First verify the job belongs to the user
    existing_job = get_job(job_id, user_id)
    if not existing_job:
        return None
    
    update_data = job_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = (
        client.table('jobs')
        .update(update_data)
        .eq('id', str(job_id))
        .eq('user_id', str(user_id))
        .execute()
    )
    return result.data[0] if result.data else None

def delete_job(job_id: UUID, user_id: UUID) -> bool:
    """Delete a job entry."""
    client = get_supabase(use_service_key=True)
    
    # First verify the job belongs to the user
    existing_job = get_job(job_id, user_id)
    if not existing_job:
        return False
    
    result = (
        client.table('jobs')
        .delete()
        .eq('id', str(job_id))
        .eq('user_id', str(user_id))
        .execute()
    )
    return bool(result.data)

def create_job_interaction(interaction: JobInteractionCreate) -> dict:
    """Create a new job interaction."""
    client = get_supabase(use_service_key=True)
    
    interaction_data = interaction.model_dump()
    interaction_data['created_at'] = datetime.utcnow().isoformat()
    interaction_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = client.table('job_interactions').insert(interaction_data).execute()
    return result.data[0]

def get_job_interactions(job_id: UUID) -> List[dict]:
    """Get all interactions for a job."""
    client = get_supabase(use_service_key=True)
    result = (
        client.table('job_interactions')
        .select('*')
        .eq('job_id', str(job_id))
        .order('interaction_date', desc=True)
        .execute()
    )
    return result.data
