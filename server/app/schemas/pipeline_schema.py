from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from uuid import UUID
from app.models.enum import (
    AgentModelEnum,
    ContentTypeEnum,
    FrequencyEnum,
    GenreEnum,
    PlatformEnum,
    TimezoneEnum,
    TopicTypeEnum,
)
from app.models.enum import AgentModelEnum, ContentTypeEnum, FrequencyEnum, GenreEnum, PlatformEnum, TimezoneEnum, TopicTypeEnum

class PipelineCreate(BaseModel):
    platform: PlatformEnum
    content_type: ContentTypeEnum
    agent_model: AgentModelEnum

    manual_review: bool = True
    additional_prompt: Optional[str]

    posting_time: str = Field(example="14:30")
    timezone: TimezoneEnum

    frequency: FrequencyEnum
    times_per_week: Optional[int]

    temperature: float = Field(ge=0, le=1)

    connected_accounts: dict
    genre: GenreEnum

    topic_type: TopicTypeEnum
    topic_value: Optional[str]

    target_regions: List[str]

    @field_validator("posting_time")
    @classmethod
    def validate_time_format(cls, v):
        try:
            hour, minute = map(int, v.split(":"))
            assert 0 <= hour < 24 and 0 <= minute < 60
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

class PipelineResponse(PipelineCreate):
    id: int
    user_id: UUID

    class Config:
        from_attributes = True
