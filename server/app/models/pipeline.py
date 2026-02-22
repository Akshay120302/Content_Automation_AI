from sqlalchemy import Time
from app.database.database import Base
from sqlalchemy import (Column, String, Boolean, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey, BigInteger)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.models.enum import (PlatformEnum, ContentTypeEnum, AgentModelEnum, FrequencyEnum, TimezoneEnum, GenreEnum, TopicTypeEnum)


class AssetUploadStatus(enum.Enum):
    """Status of asset upload process"""
    pending = "pending"           # URL generated, waiting for upload
    uploaded = "uploaded"         # File uploaded to S3, waiting for confirmation
    confirmed = "confirmed"       # Upload confirmed by client
    failed = "failed"             # Upload failed


class AssetRole(enum.Enum):
    """Role/category of the asset"""
    reference_image = "reference_image"
    reference_video = "reference_video"
    reference_audio = "reference_audio"
    reference_document = "reference_document"
    reference_other = "reference_other"


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(SQLEnum(PlatformEnum), nullable=False)
    content_type = Column(SQLEnum(ContentTypeEnum), nullable=False)
    agent_model = Column(SQLEnum(AgentModelEnum), nullable=False)

    manual_review = Column(Boolean, default=True)

    additional_prompt = Column(String, nullable=True)

    posting_time = Column(Time, nullable=False)  # "14:30"
    timezone = Column(SQLEnum(TimezoneEnum), nullable=False)

    frequency = Column(SQLEnum(FrequencyEnum), nullable=False)
    times_per_week = Column(Integer, nullable=True)

    temperature = Column(Float, default=0.5)

    connected_accounts = Column(JSON, nullable=False)
    genre = Column(SQLEnum(GenreEnum), default=GenreEnum.all)

    topic_type = Column(SQLEnum(TopicTypeEnum), nullable=False)
    topic_value = Column(String, nullable=True)

    target_regions = Column(JSON, nullable=False)

    # Video generation configuration (optional)
    video_provider = Column(String, nullable=True)
    video_model = Column(String, nullable=True)
    video_duration_seconds = Column(Integer, nullable=True)
    video_aspect_ratio = Column(String, nullable=True)
    video_fps = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to assets
    assets = relationship("PipelineAsset", back_populates="pipeline", cascade="all, delete-orphan")


class PipelineAsset(Base):
    """
    Stores metadata for files uploaded to S3 as pipeline reference materials.
    Files are uploaded directly from browser to S3 using presigned URLs.
    """
    __tablename__ = "pipeline_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # File metadata
    filename = Column(String(255), nullable=False)  # Original filename
    content_type = Column(String(100), nullable=False)  # MIME type (e.g., image/png)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    
    # S3 information
    s3_key = Column(String(512), nullable=False, unique=True)  # S3 object key/path
    s3_bucket = Column(String(100), nullable=False)  # S3 bucket name
    
    # Upload tracking
    upload_status = Column(SQLEnum(AssetUploadStatus), default=AssetUploadStatus.pending, nullable=False)
    role = Column(SQLEnum(AssetRole), default=AssetRole.reference_other, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_at = Column(DateTime(timezone=True), nullable=True)  # When upload was confirmed
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="assets")
