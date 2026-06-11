from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
import enum

from app.database.database import Base


class SocialPostStatus(enum.Enum):
    pending = "pending"
    posted = "posted"
    failed = "failed"


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    platform_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)  # encrypted blob / ciphertext
    refresh_token = Column(Text, nullable=True)  # encrypted blob / ciphertext
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    posts = relationship("SocialPost", back_populates="account", cascade="all, delete-orphan")


class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_run_id = Column(String, ForeignKey("pipeline_runs.run_id"), nullable=True, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    status = Column(SQLEnum(SocialPostStatus), nullable=False, default=SocialPostStatus.pending)
    platform_post_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    account = relationship("SocialAccount", back_populates="posts")
