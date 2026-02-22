"""
Database models for pipeline execution tracking and logging.
Extends existing models with execution state management.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

from app.database.database import Base


class PipelineRunState(str, enum.Enum):
    """Pipeline run states."""
    INIT = "INIT"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PARTIAL_FAIL = "PARTIAL_FAIL"
    RETRY = "RETRY"
    HARD_FAIL = "HARD_FAIL"
    HALTED = "HALTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PipelineRun(Base):
    """
    Pipeline execution run tracking.
    Stores complete execution history for observability.
    """
    __tablename__ = "pipeline_runs"
    
    # Primary identification
    run_id = Column(String, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # State tracking
    state = Column(SQLEnum(PipelineRunState), default=PipelineRunState.INIT, nullable=False, index=True)
    current_step = Column(String, nullable=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Execution details
    config_snapshot = Column(JSON, nullable=False)  # Pipeline config at execution time
    user_assets = Column(JSON, nullable=True)
    execution_policy = Column(JSON, nullable=True)
    
    # Results
    outputs = Column(JSON, nullable=True)  # Final outputs from all steps
    artifacts = Column(JSON, nullable=True)  # Generated files, URLs, etc.
    
    # Error tracking
    total_failures = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Celery integration
    celery_task_id = Column(String, nullable=True, index=True)
    
    # Run metadata (mapped to existing DB column `metadata`)
    run_metadata = Column("metadata", JSON, nullable=True)
    
    # Relationships
    steps = relationship("PipelineRunStep", back_populates="run", cascade="all, delete-orphan")
    events = relationship("PipelineEvent", back_populates="run", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "pipeline_id": self.pipeline_id,
            "user_id": self.user_id,
            "state": self.state.value,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "total_failures": self.total_failures,
            "error_message": self.error_message,
            "outputs": self.outputs,
            "artifacts": self.artifacts,
            "run_metadata": self.run_metadata
        }


class StepState(str, enum.Enum):
    """Step execution states."""
    PENDING = "PENDING"
    START = "START"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    RETRY = "RETRY"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"


class PipelineRunStep(Base):
    """
    Individual step execution within a pipeline run.
    Granular tracking for each agent execution.
    """
    __tablename__ = "pipeline_run_steps"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("pipeline_runs.run_id"), nullable=False, index=True)
    step_name = Column(String, nullable=False)
    agent_name = Column(String, nullable=False)
    
    # State
    state = Column(SQLEnum(StepState), default=StepState.PENDING, nullable=False)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Execution details
    retry_count = Column(Integer, default=0)
    input_summary = Column(JSON, nullable=True)
    output_summary = Column(JSON, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_type = Column(String, nullable=True)
    
    # Step metadata (mapped to existing DB column `metadata`)
    step_metadata = Column("metadata", JSON, nullable=True)
    
    # Relationships
    run = relationship("PipelineRun", back_populates="steps")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "run_id": self.run_id,
            "step_name": self.step_name,
            "agent_name": self.agent_name,
            "state": self.state.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "output_summary": self.output_summary
        }


class EventType(str, enum.Enum):
    """Event types for pipeline logging."""
    PIPELINE_CREATED = "PIPELINE_CREATED"
    PIPELINE_STARTED = "PIPELINE_STARTED"
    PIPELINE_COMPLETED = "PIPELINE_COMPLETED"
    PIPELINE_FAILED = "PIPELINE_FAILED"
    PIPELINE_HALTED = "PIPELINE_HALTED"
    PIPELINE_CANCELLED = "PIPELINE_CANCELLED"
    
    STEP_START = "STEP_START"
    STEP_SUCCESS = "STEP_SUCCESS"
    STEP_FAIL = "STEP_FAIL"
    STEP_RETRY = "STEP_RETRY"
    STEP_SKIP = "STEP_SKIP"
    STEP_TIMEOUT = "STEP_TIMEOUT"
    
    AGENT_INVOKED = "AGENT_INVOKED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    AGENT_ERROR = "AGENT_ERROR"
    
    STATE_TRANSITION = "STATE_TRANSITION"
    QUALITY_CHECK = "QUALITY_CHECK"
    RETRY_LIMIT_REACHED = "RETRY_LIMIT_REACHED"
    FAILURE_LIMIT_REACHED = "FAILURE_LIMIT_REACHED"


class LogLevel(str, enum.Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PipelineEvent(Base):
    """
    Append-only event log for pipeline execution.
    Provides complete audit trail and observability.
    """
    __tablename__ = "pipeline_events"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True, nullable=False, index=True)
    run_id = Column(String, ForeignKey("pipeline_runs.run_id"), nullable=False, index=True)
    pipeline_id = Column(String, nullable=False, index=True)
    
    # Event details
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False)
    
    # Context
    step_name = Column(String, nullable=True)
    agent_name = Column(String, nullable=True)
    state = Column(String, nullable=True)
    previous_state = Column(String, nullable=True)
    
    # Message and data
    message = Column(Text, nullable=True)
    payload = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Metrics
    duration_ms = Column(Float, nullable=True)
    retry_count = Column(Integer, nullable=True)
    
    # Additional context (mapped to existing DB column `metadata`)
    event_metadata = Column("metadata", JSON, nullable=True)
    
    # Relationships
    run = relationship("PipelineRun", back_populates="events")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "run_id": self.run_id,
            "pipeline_id": self.pipeline_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type.value,
            "level": self.level.value,
            "step_name": self.step_name,
            "agent_name": self.agent_name,
            "state": self.state,
            "previous_state": self.previous_state,
            "message": self.message,
            "payload": self.payload,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
            "event_metadata": self.event_metadata
        }


class ResearchContext(Base):
    """
    Cached research contexts for reuse.
    Stores ContextPack outputs from DeepResearchAgent.
    """
    __tablename__ = "research_contexts"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    research_id = Column(String, unique=True, nullable=False, index=True)
    
    # Research parameters
    topic = Column(String, nullable=False, index=True)
    depth = Column(String, nullable=False)
    region = Column(String, nullable=True)
    language = Column(String, default="en")
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # Research data
    context_pack = Column(JSON, nullable=False)  # Complete ContextPack as JSON
    
    # Metadata
    confidence_score = Column(Float, nullable=True)
    source_count = Column(Integer, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "research_id": self.research_id,
            "topic": self.topic,
            "depth": self.depth,
            "region": self.region,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "context_pack": self.context_pack,
            "confidence_score": self.confidence_score,
            "source_count": self.source_count
        }
