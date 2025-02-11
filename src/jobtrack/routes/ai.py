from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional
from ..core.auth import get_current_user
from ..schemas.user import User
from ..services.ai import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/analyze-resume")
async def analyze_resume(
    resume_text: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Analyze a resume using AI."""
    try:
        return await ai_service.analyze_resume(resume_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match-job")
async def match_job(
    job_description: str,
    resume_analysis: Dict,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Match a job description with a candidate's profile."""
    try:
        return await ai_service.match_job(job_description, resume_analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-cover-letter")
async def generate_cover_letter(
    job_description: str,
    resume_analysis: Dict,
    company_name: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Generate a cover letter using AI."""
    try:
        return {
            "cover_letter": await ai_service.generate_cover_letter(
                job_description, resume_analysis, company_name
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-improvements")
async def suggest_improvements(
    application_materials: Dict,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Get AI suggestions for improving application materials."""
    try:
        return await ai_service.suggest_improvements(application_materials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
