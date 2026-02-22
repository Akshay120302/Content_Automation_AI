from pydantic import BaseModel, Field, field_validator, model_validator, field_serializer
from typing import List, Optional, Union
from uuid import UUID
from datetime import time as TimeType
from app.models.enum import (
    AgentModelEnum,
    ContentTypeEnum,
    FrequencyEnum,
    GenreEnum,
    PlatformEnum,
    TimezoneEnum,
    TopicTypeEnum,
)

class PipelineCreate(BaseModel):
    platform: PlatformEnum
    content_type: ContentTypeEnum
    agent_model: AgentModelEnum

    manual_review: bool = True
    additional_prompt: Optional[str]

    posting_time: TimeType
    timezone: TimezoneEnum

    frequency: FrequencyEnum
    times_per_week: Optional[int]

    temperature: float = Field(ge=0, le=1)

    connected_accounts: dict
    genre: GenreEnum

    topic_type: TopicTypeEnum
    topic_value: Optional[str]

    target_regions: List[str]

    # Video generation settings (optional)
    video_provider: Optional[str] = None
    video_model: Optional[str] = None
    video_duration_seconds: Optional[int] = None
    video_aspect_ratio: Optional[str] = None
    video_fps: Optional[int] = None

    @field_validator("posting_time", mode="before")
    @classmethod
    def validate_time_format(cls, v):
        """Convert string to time object if needed"""
        if isinstance(v, str):
            try:
                hour, minute = map(int, v.split(":"))
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    raise ValueError("Invalid time values")
                return TimeType(hour, minute)
            except Exception:
                raise ValueError("posting_time must be in HH:MM format")
        return v

    @model_validator(mode="after")
    def validate_frequency_logic(self):
        if self.frequency == FrequencyEnum.weekly:
            if not self.times_per_week or self.times_per_week < 1:
                raise ValueError("times_per_week must be set for weekly frequency")
        else:
            if self.times_per_week is not None:
                raise ValueError("times_per_week is only valid for weekly frequency")
        return self

class PipelineResponse(BaseModel):
    id: int
    user_id: UUID
    platform: PlatformEnum
    content_type: ContentTypeEnum
    agent_model: AgentModelEnum
    manual_review: bool
    additional_prompt: Optional[str]
    posting_time: TimeType
    timezone: TimezoneEnum
    frequency: FrequencyEnum
    times_per_week: Optional[int]
    temperature: float
    connected_accounts: dict
    genre: GenreEnum
    topic_type: TopicTypeEnum
    topic_value: Optional[str]
    target_regions: List[str]

    # Video generation settings (optional)
    video_provider: Optional[str] = None
    video_model: Optional[str] = None
    video_duration_seconds: Optional[int] = None
    video_aspect_ratio: Optional[str] = None
    video_fps: Optional[int] = None

    class Config:
        from_attributes = True

    @field_serializer('posting_time')
    def serialize_posting_time(self, posting_time: TimeType, _info):
        """Serialize time object to string format HH:MM for JSON"""
        return posting_time.strftime("%H:%M")
