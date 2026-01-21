from sqlalchemy import Time
from app.database.database import Base
from sqlalchemy import (Column, String, Boolean, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.models.enum import (PlatformEnum, ContentTypeEnum, AgentModelEnum, FrequencyEnum, TimezoneEnum, GenreEnum, TopicTypeEnum)

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

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
