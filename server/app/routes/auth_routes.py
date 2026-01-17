from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User


from app.schemas.auth_schema import (UserSignupRequest, UserLoginRequest, TokenResponse, MessageResponse, RefreshTokenRequest)
from app.controllers.auth_controller import delete_user_account, resend_verification_email, signup_user, login_user, refresh_access_token, logout_all_devices, get_current_user
from app.controllers.auth_controller import verify_email_token


security = HTTPBearer()

# Dependency to get the authenticated user
def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    return get_current_user(credentials.credentials, db)

# Define the router
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Signup route
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignupRequest, db: Session = Depends(get_db)):
    return signup_user(user_data, db)


# Email verification route
@router.get("/verify-email", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    verify_email_token(token, db)
    return MessageResponse(message="Email verified successfully")


# Resend verification email route
@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    resend_verification_email(current_user, db)
    return MessageResponse(message="Verification email sent")


# Login route
@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    return login_user(login_data, db)


# Refresh token route
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    return refresh_access_token(token_data.refresh_token, db)


# Logout route
@router.post("/logout", response_model=MessageResponse)
def logout(current_user: User = Depends(get_authenticated_user), db: Session = Depends(get_db)):
    """Logout user from all devices by revoking all refresh tokens"""
    logout_all_devices(current_user.id, db)
    return MessageResponse(message="Successfully logged out from all devices")


# Delete account route
@router.delete("/me", response_model=MessageResponse)
def delete_my_account(current_user: User = Depends(get_authenticated_user), db: Session = Depends(get_db)):
    """Delete the authenticated user's account"""
    delete_user_account(current_user.id, db)
    return MessageResponse(message="User account deleted successfully")


# Test route
@router.get("/test", response_model=MessageResponse)
def test_auth():
    """Test authentication endpoint"""
    return MessageResponse(message="Auth routes are working!")
