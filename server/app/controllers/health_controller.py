from datetime import datetime
from app.config import settings


class HealthController:
    """Controller for health check endpoints"""
    
    @staticmethod
    def get_health_status():
        """
        Get the health status of the application
        
        Returns:
            dict: Health status information
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.APP_NAME,
            "version": settings.VERSION
        }
    
    @staticmethod
    def get_root_info():
        """
        Get root endpoint information
        
        Returns:
            dict: API information
        """
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "status": "running",
            "version": settings.VERSION,
            "docs": "/docs",
            "health": "/health"
        }
