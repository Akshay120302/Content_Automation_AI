"""
Structured logging and observability system for pipeline execution.
Provides append-only event logs with comprehensive tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from pathlib import Path


class LogLevel(str, Enum):
    """Log levels for pipeline events."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventType(str, Enum):
    """Types of pipeline events."""
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


@dataclass
class PipelineEvent:
    """Structured event for pipeline execution."""
    event_id: str
    pipeline_run_id: str
    pipeline_id: str
    timestamp: datetime
    event_type: EventType
    level: LogLevel
    step_name: Optional[str] = None
    agent_name: Optional[str] = None
    state: Optional[str] = None
    previous_state: Optional[str] = None
    message: str = ""
    payload: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    retry_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        data = asdict(self)
        # Convert datetime to ISO format
        data['timestamp'] = self.timestamp.isoformat()
        # Convert enums to values
        data['event_type'] = self.event_type.value
        data['level'] = self.level.value
        return data
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class PipelineLogger:
    """
    Structured logger for pipeline execution.
    Provides append-only event logging with multiple outputs.
    """
    
    def __init__(
        self,
        pipeline_run_id: str,
        pipeline_id: str,
        log_file: Optional[Path] = None,
        enable_console: bool = True
    ):
        self.pipeline_run_id = pipeline_run_id
        self.pipeline_id = pipeline_id
        self.log_file = log_file
        self.enable_console = enable_console
        self.event_counter = 0
        
        # Set up Python logger
        self.logger = logging.getLogger(f"pipeline.{pipeline_run_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # Add console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        self.event_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return f"{self.pipeline_run_id}_{timestamp}_{self.event_counter}"
    
    def log_event(self, event: PipelineEvent) -> None:
        """
        Log a pipeline event.
        
        Args:
            event: PipelineEvent to log
        """
        # Log to Python logger
        log_msg = self._format_event_message(event)
        
        if event.level == LogLevel.DEBUG:
            self.logger.debug(log_msg)
        elif event.level == LogLevel.INFO:
            self.logger.info(log_msg)
        elif event.level == LogLevel.WARNING:
            self.logger.warning(log_msg)
        elif event.level == LogLevel.ERROR:
            self.logger.error(log_msg)
        elif event.level == LogLevel.CRITICAL:
            self.logger.critical(log_msg)
        
        # TODO: Send to database/event store
        # This would integrate with your database models
    
    def _format_event_message(self, event: PipelineEvent) -> str:
        """Format event for logging."""
        parts = [f"[{event.event_type.value}]"]
        
        if event.step_name:
            parts.append(f"Step: {event.step_name}")
        if event.agent_name:
            parts.append(f"Agent: {event.agent_name}")
        if event.state:
            parts.append(f"State: {event.state}")
        if event.message:
            parts.append(event.message)
        if event.error:
            parts.append(f"Error: {event.error}")
        
        return " | ".join(parts)
    
    def pipeline_started(self, config: Dict[str, Any]) -> None:
        """Log pipeline start event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.PIPELINE_STARTED,
            level=LogLevel.INFO,
            message=f"Pipeline execution started",
            payload={"config_summary": config}
        )
        self.log_event(event)
    
    def pipeline_completed(self, duration_ms: float) -> None:
        """Log pipeline completion event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.PIPELINE_COMPLETED,
            level=LogLevel.INFO,
            message=f"Pipeline completed successfully",
            duration_ms=duration_ms
        )
        self.log_event(event)
    
    def pipeline_failed(self, error: str, duration_ms: float) -> None:
        """Log pipeline failure event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.PIPELINE_FAILED,
            level=LogLevel.ERROR,
            message=f"Pipeline failed",
            error=error,
            duration_ms=duration_ms
        )
        self.log_event(event)
    
    def step_start(self, step_name: str, agent_name: str) -> None:
        """Log step start event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STEP_START,
            level=LogLevel.INFO,
            step_name=step_name,
            agent_name=agent_name,
            message=f"Starting step: {step_name}"
        )
        self.log_event(event)
    
    def step_success(
        self,
        step_name: str,
        agent_name: str,
        duration_ms: float,
        summary: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log step success event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STEP_SUCCESS,
            level=LogLevel.INFO,
            step_name=step_name,
            agent_name=agent_name,
            message=f"Step completed successfully: {step_name}",
            duration_ms=duration_ms,
            payload=summary
        )
        self.log_event(event)
    
    def step_fail(
        self,
        step_name: str,
        agent_name: str,
        error: str,
        retry_count: int
    ) -> None:
        """Log step failure event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STEP_FAIL,
            level=LogLevel.ERROR,
            step_name=step_name,
            agent_name=agent_name,
            message=f"Step failed: {step_name}",
            error=error,
            retry_count=retry_count
        )
        self.log_event(event)
    
    def step_retry(self, step_name: str, agent_name: str, retry_count: int) -> None:
        """Log step retry event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STEP_RETRY,
            level=LogLevel.WARNING,
            step_name=step_name,
            agent_name=agent_name,
            message=f"Retrying step: {step_name} (attempt {retry_count})",
            retry_count=retry_count
        )
        self.log_event(event)
    
    def state_transition(
        self,
        previous_state: str,
        new_state: str,
        reason: Optional[str] = None
    ) -> None:
        """Log state transition event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STATE_TRANSITION,
            level=LogLevel.INFO,
            previous_state=previous_state,
            state=new_state,
            message=f"State transition: {previous_state} → {new_state}",
            payload={"reason": reason} if reason else None
        )
        self.log_event(event)
    
    def quality_check(
        self,
        status: str,
        score: float,
        reasons: List[str]
    ) -> None:
        """Log quality check event."""
        event = PipelineEvent(
            event_id=self._generate_event_id(),
            pipeline_run_id=self.pipeline_run_id,
            pipeline_id=self.pipeline_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.QUALITY_CHECK,
            level=LogLevel.INFO if status == "PASS" else LogLevel.WARNING,
            message=f"Quality check: {status} (score: {score})",
            payload={"status": status, "score": score, "reasons": reasons}
        )
        self.log_event(event)


class LogAggregator:
    """Aggregates and queries pipeline logs."""
    
    def __init__(self):
        self.events: List[PipelineEvent] = []
    
    def add_event(self, event: PipelineEvent) -> None:
        """Add event to aggregator."""
        self.events.append(event)
    
    def get_events_by_type(self, event_type: EventType) -> List[PipelineEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_by_step(self, step_name: str) -> List[PipelineEvent]:
        """Get all events for a specific step."""
        return [e for e in self.events if e.step_name == step_name]
    
    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get chronological timeline of events."""
        return [e.to_dict() for e in sorted(self.events, key=lambda x: x.timestamp)]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            "total_events": len(self.events),
            "event_types": {
                event_type.value: len(self.get_events_by_type(event_type))
                for event_type in EventType
            },
            "steps": list(set(e.step_name for e in self.events if e.step_name)),
            "agents": list(set(e.agent_name for e in self.events if e.agent_name))
        }
