from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
import sys


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Content Automation AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, production
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    
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
    Backend_URL: str = "http://127.0.0.1:8000"
    
    # API Keys (for external services)
    OPENAI_API_KEY: str = ""
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = ""
    S3_PRESIGNED_URL_EXPIRY: int = 900  # 15 minutes (in seconds)
    S3_MAX_FILE_SIZE: int = 52428800  # 50MB (in bytes)

    # Redis URL (for local Redis on port 6379)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Redis connection details (for Celery)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # AI/ML API Keys
    ANTHROPIC_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    RUNWAY_API_KEY: str = ""
    RUNWAY_API_URL: str = ""
    COMFYUI_URL: str = "http://localhost:8188"
    VIDEO_PROVIDER: str = "replicate"
    
    # LangChain settings
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "false"
    
    # Security settings
    REQUIRE_EMAIL_VERIFICATION: bool = True  # Block app access until email verified
    ENABLE_CSRF_PROTECTION: bool = True  # CSRF protection for cookie-based auth
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def validate_settings(self):
        """Validate critical security settings"""
        errors = []
        
        # Check SECRET_KEY
        if self.SECRET_KEY in ["give-your-secret-key-here", "your-secret-key-here", "secret", "change-me"]:
            errors.append(
                "🔴 CRITICAL: SECRET_KEY is using default/weak value. "
                "Generate a strong key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        if len(self.SECRET_KEY) < 32:
            errors.append(
                "⚠️  WARNING: SECRET_KEY should be at least 32 characters long for security"
            )
        
        # Check DATABASE_URL
        if "strictly replace" in self.DATABASE_URL.lower():
            errors.append(
                "🔴 CRITICAL: DATABASE_URL is not configured. Set it in .env file"
            )
        
        # Production-specific checks
        if self.is_production:
            if self.DEBUG:
                errors.append("⚠️  WARNING: DEBUG mode is enabled in production")
            
            if "localhost" in self.DATABASE_URL:
                errors.append("⚠️  WARNING: Using localhost database in production")
        
        # Display errors
        if errors:
            print("\n" + "="*70)
            print("⚠️  CONFIGURATION WARNINGS")
            print("="*70)
            for error in errors:
                print(error)
            print("="*70 + "\n")
            
            # Exit on critical errors in production
            if self.is_production and any("CRITICAL" in e for e in errors):
                print("❌ Cannot start server with critical configuration errors in production")
                sys.exit(1)


settings = Settings()

# Validate settings on import
settings.validate_settings()
