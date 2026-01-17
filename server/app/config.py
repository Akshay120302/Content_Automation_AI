from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Content Automation AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Database settings - Neon PostgreSQL
    # Format: postgresql://username:password@host/database?sslmode=require
    DATABASE_URL: str = "strictly replace with your database url"
    
    # JWT/Auth settings
    SECRET_KEY: str = "give-your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # EMAIL VERIFCATION TOKEN TIME LIMIT
    EMAIL_VERIFY_EXP_HOURS: int = 24

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://127.0.0.1:8000"
    
    # API Keys (for external services)
    OPENAI_API_KEY: str = ""
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
