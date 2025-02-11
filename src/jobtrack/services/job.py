from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..core.supabase import get_supabase
from ..schemas.job import (
    Job,
    JobCreate,
    JobUpdate,
    JobInteraction,
    JobInteractionCreate,
    Company,
    CompanyCreate,
    JobApplication,
    JobApplicationCreate,
    JobApplicationWithDetails,
    Interaction,
    InteractionCreate,
    Skill,
    SkillCreate
)

class JobService:
    def __init__(self):
        self.client = get_supabase()

    def create_company(self, company: CompanyCreate) -> Company:
        data = {
            **company.model_dump(),
            'created_at': datetime.utcnow()
        }
        result = self.client.table('companies').insert(data).execute()
        return Company(**result.data[0])

    def create_job_application(self, application: JobApplicationCreate, user_id: int) -> JobApplication:
        data = {
            **application.model_dump(),
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = self.client.table('job_applications').insert(data).execute()
        return JobApplication(**result.data[0])

    def get_user_applications(self, user_id: int) -> List[JobApplicationWithDetails]:
        result = (self.client
                 .table('job_applications')
                 .select('*, company:companies(*), interactions(*), skills(*)')
                 .eq('user_id', user_id)
                 .order('created_at', desc=True)
                 .execute())
        return [JobApplicationWithDetails(**app) for app in result.data]

    def create_interaction(self, interaction: InteractionCreate) -> Interaction:
        data = {
            **interaction.model_dump(),
            'created_at': datetime.utcnow()
        }
        result = self.client.table('interactions').insert(data).execute()
        return Interaction(**result.data[0])

    def get_application_interactions(self, application_id: int) -> List[Interaction]:
        result = (self.client
                 .table('interactions')
                 .select('*')
                 .eq('job_application_id', application_id)
                 .order('created_at', desc=True)
                 .execute())
        return [Interaction(**interaction) for interaction in result.data]

    def create_skill(self, skill: SkillCreate) -> Skill:
        data = {
            **skill.model_dump(),
            'created_at': datetime.utcnow()
        }
        result = self.client.table('skills').insert(data).execute()
        return Skill(**result.data[0])

    def add_skills_to_application(self, application_id: int, skill_ids: List[int]) -> None:
        data = [
            {'job_application_id': application_id, 'skill_id': skill_id}
            for skill_id in skill_ids
        ]
        self.client.table('job_application_skills').insert(data).execute()

    def update_application_status(self, application_id: int, status: str) -> JobApplication:
        data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        result = (self.client
                 .table('job_applications')
                 .update(data)
                 .eq('id', application_id)
                 .execute())
        return JobApplication(**result.data[0])

    def get_application_stats(self, user_id: int) -> dict:
        applications = (self.client
                       .table('job_applications')
                       .select('status')
                       .eq('user_id', user_id)
                       .execute())
        
        stats = {
            'total': len(applications.data),
            'status_counts': {}
        }
        
        for app in applications.data:
            status = app['status']
            if status in stats['status_counts']:
                stats['status_counts'][status] += 1
            else:
                stats['status_counts'][status] = 1
            
        return stats

    def create_job(self, user_id: str, job: JobCreate) -> Job:
        """Create a new job entry."""
        job_dict = job.model_dump()
        job_dict.update({
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        result = self.client.table('jobs').insert(job_dict).execute()
        return Job(**result.data[0])

    def get_user_jobs(self, user_id: str) -> List[Job]:
        """Get all jobs for a user."""
        result = self.client.table('jobs').select('*').eq('user_id', user_id).execute()
        return [Job(**job) for job in result.data]

    def get_job(self, job_id: UUID, user_id: str) -> Optional[Job]:
        """Get a specific job."""
        result = self.client.table('jobs').select('*').eq('id', str(job_id)).eq('user_id', user_id).execute()
        jobs = result.data
        return Job(**jobs[0]) if jobs else None

    def update_job(self, job_id: UUID, user_id: str, job_update: JobUpdate) -> Optional[Job]:
        """Update a job entry."""
        # Verify job exists and belongs to user
        if not self.get_job(job_id, user_id):
            return None
        
        update_dict = job_update.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.utcnow()
        
        result = self.client.table('jobs').update(update_dict).eq('id', str(job_id)).execute()
        return Job(**result.data[0])

    def delete_job(self, job_id: UUID, user_id: str) -> bool:
        """Delete a job entry."""
        # Verify job exists and belongs to user
        if not self.get_job(job_id, user_id):
            return False
        
        self.client.table('jobs').delete().eq('id', str(job_id)).execute()
        return True

    def create_job_interaction(self, interaction: JobInteractionCreate) -> JobInteraction:
        """Create a new job interaction."""
        interaction_dict = interaction.model_dump()
        interaction_dict.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        result = self.client.table('job_interactions').insert(interaction_dict).execute()
        return JobInteraction(**result.data[0])

    def get_job_interactions(self, job_id: UUID) -> List[JobInteraction]:
        """Get all interactions for a job."""
        result = self.client.table('job_interactions').select('*').eq('job_id', str(job_id)).execute()
        return [JobInteraction(**interaction) for interaction in result.data]


# Initialize job service
job_service = JobService()

# Export functions that use the service
def create_job(user_id: str, job: JobCreate) -> Job:
    return job_service.create_job(user_id, job)

def get_user_jobs(user_id: str) -> List[Job]:
    return job_service.get_user_jobs(user_id)

def get_job(job_id: UUID, user_id: str) -> Optional[Job]:
    return job_service.get_job(job_id, user_id)

def update_job(job_id: UUID, user_id: str, job_update: JobUpdate) -> Optional[Job]:
    return job_service.update_job(job_id, user_id, job_update)

def delete_job(job_id: UUID, user_id: str) -> bool:
    return job_service.delete_job(job_id, user_id)

def create_job_interaction(interaction: JobInteractionCreate) -> JobInteraction:
    return job_service.create_job_interaction(interaction)

def get_job_interactions(job_id: UUID) -> List[JobInteraction]:
    return job_service.get_job_interactions(job_id)
