from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7
from app.database.database import Base


class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Plan(Base):
    """Subscription plan model"""
    __tablename__ = "plans"
    
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, index=True)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    features = Column(JSON, nullable=False, default=lambda: {})

    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"
    
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, index=True)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active")  # active, expired, cancelled
    expires_at = Column(DateTime(timezone=True), nullable=True)
    gateway_subscription_id = Column(String(255), nullable=True, unique=True)  # Payment gateway subscription ID
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class RefreshToken(Base):
    """Refresh token model for JWT authentication"""
    __tablename__ = "refresh_tokens"
    
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, index=True)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class OAuthAccount(Base):
    """OAuth account model for social login (Google, GitHub, etc.)"""
    __tablename__ = "oauth_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # google, github, etc.
    provider_user_id = Column(String(255), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="oauth_accounts")
