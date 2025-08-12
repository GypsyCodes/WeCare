"""
Configuration settings for We Care system
"""
from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "We Care - Sistema de Gestão Operacional"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "wecare-secret-key-2024-development-only-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "wecare"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    
    @property
    def MYSQL_DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Security Configuration
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Storage Configuration
    UPLOAD_PATH: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".jpg", ".jpeg", ".png"]
    
    # AI/OCR Configuration
    TESSERACT_PATH: Optional[str] = None
    SPACY_MODEL: str = "pt_core_news_sm"
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Monitoring Configuration
    SENTRY_DSN: Optional[str] = None
    
    # Business Logic Configuration
    CHECKIN_WINDOW_MINUTES: int = 15  # Check-in allowed 15 minutes before shift
    GPS_TOLERANCE_METERS: int = 100   # GPS tolerance for location validation
    TOKEN_EXPIRE_HOURS: int = 24      # Registration token expiration
    

    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 