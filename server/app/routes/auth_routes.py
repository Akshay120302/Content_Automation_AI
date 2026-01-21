from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.auth_schema import (UserSignupRequest, UserLoginRequest, TokenResponse, MessageResponse)
from app.controllers.auth_controller import delete_user_account, resend_verification_email, signup_user, login_user, refresh_access_token, logout_all_devices, get_current_user
from app.controllers.auth_controller import verify_email_token
from app.utils.rate_limit import signup_rate_limit, login_rate_limit, refresh_rate_limit


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
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(signup_rate_limit)])
def signup(user_data: UserSignupRequest, response: Response, db: Session = Depends(get_db)):
    return signup_user(user_data, db, response)


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
@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def login(login_data: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    return login_user(login_data, db, response)


# Refresh token route
@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(refresh_rate_limit)])
def refresh_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    return refresh_access_token(refresh_token, db, response)


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
