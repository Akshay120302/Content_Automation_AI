"""
CSRF Protection utilities for cookie-based authentication
"""
import secrets
from fastapi import HTTPException, status, Response, Request
from app.config import settings


def generate_csrf_token() -> str:
    """Generate a secure CSRF token"""
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response: Response, csrf_token: str):
    """Set CSRF token in a readable cookie (double-submit pattern)"""
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  # Must be readable by JavaScript
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="strict",
        path="/",
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS
    )


def verify_csrf_token(request: Request, csrf_header: str = None):
    """
    Verify CSRF token using double-submit cookie pattern
    
    Args:
        request: FastAPI request object
        csrf_header: CSRF token from request header
        
    Raises:
        HTTPException: If CSRF validation fails
    """
    # Get CSRF token from cookie
    csrf_cookie = request.cookies.get("csrf_token")
    
    # For state-changing operations (POST, PUT, DELETE), verify CSRF
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        if not csrf_cookie or not csrf_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        if csrf_cookie != csrf_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token mismatch"
            )
    
    return True
