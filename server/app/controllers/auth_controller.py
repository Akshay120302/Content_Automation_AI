from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi import Response
import secrets
import uuid

from app.models.user import EmailVerificationToken, User, RefreshToken
from app.config import settings
from app.schemas.auth_schema import UserSignupRequest, UserLoginRequest, TokenResponse, UserResponse
from app.utils.email_verification import send_verification_email
from app.database.redis_client import get_redis
from app.utils.password_validator import validate_password_strength
from app.utils.csrf_protection import generate_csrf_token, set_csrf_cookie


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
def create_refresh_token(user_id: UUID, db: Session) -> tuple[str, str]:
    """
    Create a refresh token and store it in Redis (or database as fallback)
    Returns: (token, token_id)
    """
    redis = get_redis()
    
    # Generate a secure random token and unique ID
    token = secrets.token_urlsafe(32)
    token_id = str(uuid.uuid4())
    token_hash = hash_password(token)
    
    # Set expiry (7 days)
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    
    # Try to store in Redis first
    if redis.is_available():
        success = redis.store_refresh_token(
            token_id=token_id,
            user_id=str(user_id),
            token_hash=token_hash,
            ttl_seconds=ttl_seconds
        )
        if success:
            return token, token_id
    
    # Fallback to database if Redis is unavailable
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False
    )
    
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    
    return token, str(refresh_token.id)

# Set refresh token in HttpOnly cookie
def set_refresh_cookie(response: Response, refresh_token: str, token_id: str):
    """Set refresh token in HttpOnly cookie with token ID"""
    # Store both token and token_id in cookie (separated by :)
    cookie_value = f"{token_id}:{refresh_token}"
    
    response.set_cookie(
        key="refresh_token",
        value=cookie_value,
        httponly=True,
        secure=settings.is_production,  # HTTPS only in production
        samesite="strict" if settings.is_production else "lax",
        path="/auth/refresh",
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS
    )


# Signup Controller
def signup_user(user_data: UserSignupRequest, db: Session, response: Response) -> TokenResponse:
    """
    Register a new user
    """
    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
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
    
    # SECURITY: Only provide tokens if email verification is not required
    if settings.REQUIRE_EMAIL_VERIFICATION:
        # Don't provide tokens until email is verified
        return TokenResponse(
            access_token="",  # No token until verified
            refresh_token="",
            token_type="bearer",
            user=UserResponse.model_validate(new_user)
        )
    
    # Create access token and refresh token (only if verification not required)
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token, token_id = create_refresh_token(new_user.id, db)

    set_refresh_cookie(response, refresh_token, token_id)
    
    # Set CSRF token
    if settings.ENABLE_CSRF_PROTECTION:
        csrf_token = generate_csrf_token()
        set_csrf_cookie(response, csrf_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token="",  # refresh token is set in HttpOnly cookie and frontend does not need it directly
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


# Login Controller
def login_user(login_data: UserLoginRequest, db: Session, response: Response) -> TokenResponse:
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

    # Clean up old expired tokens for this user to prevent accumulation
    redis = get_redis()
    if redis.is_available():
        redis.cleanup_expired_user_tokens(str(user.id))
    
    # Create access token and refresh token
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token, token_id = create_refresh_token(user.id, db)

    set_refresh_cookie(response, refresh_token, token_id)
    
    # Set CSRF token
    if settings.ENABLE_CSRF_PROTECTION:
        csrf_token = generate_csrf_token()
        set_csrf_cookie(response, csrf_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token="",  # refresh token is set in HttpOnly cookie and frontend does not need it directly
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
def refresh_access_token(refresh_token_cookie: str, db: Session, response: Response) -> TokenResponse:
    """
    Generate a new access token using a refresh token from Redis or database
    """
    redis = get_redis()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Parse cookie value (format: "token_id:token")
    try:
        token_id, refresh_token = refresh_token_cookie.split(":", 1)
    except ValueError:
        raise credentials_exception
    
    # Try Redis first
    if redis.is_available():
        token_data = redis.get_refresh_token(token_id)
        
        if token_data and not token_data["revoked"]:
            # Verify token hash
            if verify_password(refresh_token, token_data["token_hash"]):
                user_id = UUID(token_data["user_id"])
                
                # Get the user
                user = db.query(User).filter(User.id == user_id).first()
                if not user or not user.is_active:
                    raise credentials_exception
                
                # Create new access token
                access_token = create_access_token(data={"sub": str(user.id)})
                
                # Check if token should be rotated (only if close to expiry)
                # Get TTL from Redis
                ttl = redis.get_token_ttl(token_id)
                should_rotate = ttl and ttl < (24 * 60 * 60)  # Less than 24 hours remaining
                
                if should_rotate:
                    # Rotate refresh token only when close to expiry
                    redis.delete_refresh_token(token_id)
                    new_refresh_token, new_token_id = create_refresh_token(user.id, db)
                    set_refresh_cookie(response, new_refresh_token, new_token_id)
                else:
                    # Reuse the same refresh token - just reset the cookie
                    set_refresh_cookie(response, refresh_token, token_id)
                
                return TokenResponse(
                    access_token=access_token,
                    refresh_token="",
                    token_type="bearer",
                    user=UserResponse.model_validate(user)
                )
    
    # Fallback to database
    refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.id == int(token_id) if token_id.isdigit() else -1,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).all()
    
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
    
    # Check if token should be rotated (only if close to expiry)
    time_until_expiry = matched_token.expires_at - datetime.utcnow()
    should_rotate = time_until_expiry.total_seconds() < (24 * 60 * 60)  # Less than 24 hours
    
    if should_rotate:
        # Rotate refresh token only when close to expiry
        matched_token.revoked = True
        db.commit()
        
        new_refresh_token, new_token_id = create_refresh_token(user.id, db)
        set_refresh_cookie(response, new_refresh_token, new_token_id)
    else:
        # Reuse the same refresh token - just reset the cookie
        set_refresh_cookie(response, refresh_token, token_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token="",
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# Logout from all devices
def logout_all_devices(user_id: UUID, db: Session) -> None:
    """
    Revoke all refresh tokens for a user (logout from all devices)
    Works with both Redis and database
    """
    redis = get_redis()
    
    # Revoke from Redis
    if redis.is_available():
        redis.delete_all_user_tokens(str(user_id))
    
    # Also revoke from database (fallback + cleanup)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()


# Logout from single device
def logout_current_device(token_id: str, db: Session) -> None:
    """
    Revoke only the current device's refresh token
    """
    redis = get_redis()
    
    # Delete from Redis
    if redis.is_available():
        redis.delete_refresh_token(token_id)
    
    # Also delete from database if token_id is numeric (DB ID)
    if token_id.isdigit():
        db.query(RefreshToken).filter(
            RefreshToken.id == int(token_id)
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
