from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Supabase settings
    supabase_url: str = Field(..., env='SUPABASE_URL')
    supabase_key: str = Field(..., env='SUPABASE_KEY')
    supabase_secret_key: str = Field(..., env='SUPABASE_SECRET_KEY')
    
    # JWT settings
    secret_key: str = Field(..., env='SECRET_KEY')
    algorithm: str = Field('HS256', env='ALGORITHM')
    access_token_expire_minutes: int = Field(30, env='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_expire_days: int = Field(7, env='REFRESH_TOKEN_EXPIRE_DAYS')
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env='CORS_ORIGINS'
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
