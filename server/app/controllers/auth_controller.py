from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import secrets

from app.models.user import EmailVerificationToken, User, RefreshToken
from app.config import settings
from app.schemas.auth_schema import UserSignupRequest, UserLoginRequest, TokenResponse, UserResponse
from app.utils.email_verification import send_verification_email


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash password
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Create refresh token
def create_refresh_token(user_id: UUID, db: Session) -> str:
    """Create a refresh token and store it in the database"""
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    token_hash = hash_password(token)
    
    # Set expiry
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store in database
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False
    )
    
    db.add(refresh_token)
    db.commit()
    
    return token


# Signup Controller
def signup_user(user_data: UserSignupRequest, db: Session) -> TokenResponse:
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        username=user_data.username,
        is_verified=False,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Email verification token can be created here if needed
    raw_token = create_email_verification_token(new_user.id, db)
    verification_link = (f"{settings.FRONTEND_URL}/verify-email?token={raw_token}")
    send_verification_email(to_email=new_user.email, verification_link=verification_link)
    
    # Create access token and refresh token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(new_user.id, db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


# Login Controller
def login_user(login_data: UserLoginRequest, db: Session) -> TokenResponse:
    """
    Authenticate and login a user
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check if user is verified (email verfified or not)
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )

    
    # Create access token and refresh token
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(user.id, db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# Get current user from token
def get_current_user(token: str, db: Session) -> User:
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


# Refresh the Access Token
def refresh_access_token(refresh_token: str, db: Session) -> TokenResponse:
    """
    Generate a new access token using a refresh token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Find all refresh tokens and check which one matches
    refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).all()
    
    # assume no valid token exists until proven otherwise
    matched_token = None
    for rt in refresh_tokens:
        if verify_password(refresh_token, rt.token_hash):
            matched_token = rt
            break
    
    if not matched_token:
        raise credentials_exception
    
    # Get the user
    user = db.query(User).filter(User.id == matched_token.user_id).first()
    if not user or not user.is_active:
        raise credentials_exception
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Rotate refresh token (optional but recommended for security)
    # Revoke old token
    matched_token.revoked = True
    db.commit()
    
    # Create new refresh token
    new_refresh_token = create_refresh_token(user.id, db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# Logout from all devices
def logout_all_devices(user_id: UUID, db: Session) -> None:
    """
    Revoke all refresh tokens for a user (logout from all devices)
    """
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()


# Delete the authenticated user account
def delete_user_account(user_id: UUID, db: Session) -> None:
    """
    Permanently delete a user and all related data
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()


# Create email verification token (used after signup)
def create_email_verification_token(user_id: UUID, db: Session) -> str:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_password(raw_token)

    token = EmailVerificationToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFY_EXP_HOURS),
        used=False
    )

    db.add(token)
    db.commit()

    return raw_token


# Verify email token
def verify_email_token(raw_token: str, db: Session):
    tokens = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.used == False,
        EmailVerificationToken.expires_at > datetime.utcnow()
    ).all()

    matched_token = None
    for t in tokens:
        if verify_password(raw_token, t.token_hash):
            matched_token = t
            break

    if not matched_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link"
        )

    user = db.query(User).filter(User.id == matched_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mark verified
    user.is_verified = True
    matched_token.used = True

    db.commit()


# Resend verification email
def resend_verification_email(user: User, db: Session):
    # 1. If already verified → do nothing
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # 2. Invalidate old unused tokens
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used == False
    ).update({"used": True})

    db.commit()

    # 3. Create new verification token
    raw_token = create_email_verification_token(user.id, db)

    # 4. Build verification link
    verification_link = (
        f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"
    )

    # 5. Send email
    send_verification_email(
        to_email=user.email,
        verification_link=verification_link
    )
