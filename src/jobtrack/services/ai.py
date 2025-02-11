from typing import Dict, List, Optional
from openai import OpenAI
from ..core.config import settings

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature

    async def analyze_resume(self, resume_text: str) -> Dict:
        """Analyze a resume and extract key information."""
        system_prompt = """You are an expert resume analyzer. Extract and organize the following information from the resume:
        1. Skills (technical and soft skills)
        2. Experience (company names, titles, dates, and key achievements)
        3. Education
        4. Key strengths
        5. Suggested job titles to search for
        
        Format the response as a JSON object."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": resume_text}
            ],
            temperature=self.temperature,
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content

    async def match_job(self, job_description: str, resume_analysis: Dict) -> Dict:
        """Analyze how well a job matches with the candidate's profile."""
        system_prompt = """You are an expert job matcher. Analyze the job description and the candidate's profile to:
        1. Calculate a match percentage
        2. List matching skills
        3. List missing skills
        4. Provide specific recommendations for the application
        
        Format the response as a JSON object."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Job Description: {job_description}\n\nCandidate Profile: {resume_analysis}"}
            ],
            temperature=self.temperature,
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content

    async def generate_cover_letter(self, job_description: str, resume_analysis: Dict, company_name: str) -> str:
        """Generate a customized cover letter based on the job and candidate's profile."""
        system_prompt = """You are an expert cover letter writer. Write a professional, compelling cover letter that:
        1. Is tailored to the specific job and company
        2. Highlights relevant skills and experiences
        3. Shows enthusiasm and cultural fit
        4. Maintains a professional yet personable tone
        
        Format the letter with proper business letter structure."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Company: {company_name}\nJob Description: {job_description}\nCandidate Profile: {resume_analysis}"}
            ],
            temperature=self.temperature
        )
        
        return response.choices[0].message.content

    async def suggest_improvements(self, application_materials: Dict) -> Dict:
        """Suggest improvements for resume, cover letter, and application strategy."""
        system_prompt = """You are an expert career coach. Analyze the application materials and provide:
        1. Resume improvement suggestions
        2. Cover letter improvement suggestions
        3. Overall application strategy recommendations
        4. Interview preparation tips
        
        Format the response as a JSON object."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(application_materials)}
            ],
            temperature=self.temperature,
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content


# Initialize AI service
ai_service = AIService()
