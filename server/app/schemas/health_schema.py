from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: datetime
    service: str
    version: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-01-11T12:00:00",
                "service": "Content Automation AI",
                "version": "1.0.0"
            }
        }


class RootResponse(BaseModel):
    """Schema for root endpoint response"""
    message: str
    status: str
    version: str
    docs: str
    health: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Welcome to Content Automation AI",
                "status": "running",
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/health"
            }
        }
