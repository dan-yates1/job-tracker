from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    supabase_url: str = Field(..., env='SUPABASE_URL')
    supabase_key: str = Field(..., env='SUPABASE_KEY')
    supabase_secret_key: str = Field(..., env='SUPABASE_SECRET_KEY')
    secret_key: str = Field(..., env='SECRET_KEY')
    algorithm: str = Field('HS256', env='ALGORITHM')
    access_token_expire_minutes: int = Field(30, env='ACCESS_TOKEN_EXPIRE_MINUTES')

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()