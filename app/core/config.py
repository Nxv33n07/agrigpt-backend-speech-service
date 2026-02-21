import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings and environment variables.
    Using pydantic-settings for validation and automatic env loading.
    """
    PROJECT_NAME: str = "AgriGPT Speech Service"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    
    # CORS Origins - specify frontend URLs here in production
    CORS_ORIGINS: list[str] = ["*"]
    
    # AI API Keys
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Post-processing to ensure we have a key if either is provided
if not settings.GOOGLE_API_KEY and settings.GEMINI_API_KEY:
    settings.GOOGLE_API_KEY = settings.GEMINI_API_KEY
elif not settings.GEMINI_API_KEY and settings.GOOGLE_API_KEY:
    settings.GEMINI_API_KEY = settings.GOOGLE_API_KEY
