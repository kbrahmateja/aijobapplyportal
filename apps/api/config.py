import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5433/aijobapply")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Clerk Authentication
    CLERK_ISSUER: str = os.getenv("CLERK_ISSUER", "") # e.g., https://clerk.your-domain.com
    CLERK_API_KEY: str = os.getenv("CLERK_API_KEY", "") 
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
