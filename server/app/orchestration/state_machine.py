"""
Pipeline state machine and state transitions.
Deterministic state management for pipeline execution.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field


class PipelineState(str, Enum):
    """Pipeline execution states."""
    INIT = "INIT"
    RUNNING = "RUNNING"
    PARTIAL_FAIL = "PARTIAL_FAIL"
    RETRY = "RETRY"
    HARD_FAIL = "HARD_FAIL"
    HALTED = "HALTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class StepState(str, Enum):
    """Individual step execution states."""
    PENDING = "PENDING"
    START = "START"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    RETRY = "RETRY"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"


class FailurePolicy(str, Enum):
    """Failure handling policies."""
    RETRY = "RETRY"
    SKIP = "SKIP"
    HALT = "HALT"
    CONTINUE = "CONTINUE"


@dataclass
class ExecutionPolicy:
    """Execution policies and limits for pipeline runs."""
    max_retries_per_step: int = 2
    max_total_failures: int = 5
    max_runtime_minutes: int = 30
    step_timeout_seconds: int = 300
    enable_parallel_execution: bool = True
    failure_policy: FailurePolicy = FailurePolicy.RETRY


@dataclass
class StepMetrics:
    """Metrics for a single step execution."""
    step_name: str
    agent_name: str
    state: StepState
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    payload_summary: Optional[Dict[str, Any]] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class PipelineExecutionState:
    """Complete state of a pipeline execution."""
    pipeline_run_id: str
    pipeline_id: str
    state: PipelineState = PipelineState.INIT
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_failures: int = 0
    current_step: Optional[str] = None
    step_metrics: Dict[str, StepMetrics] = field(default_factory=dict)
    context_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    @property
    def is_terminal(self) -> bool:
        """Check if pipeline is in a terminal state."""
        return self.state in [
            PipelineState.COMPLETED,
            PipelineState.HARD_FAIL,
            PipelineState.HALTED,
            PipelineState.CANCELLED
        ]
    
    @property
    def is_failed(self) -> bool:
        """Check if pipeline has failed."""
        return self.state in [
            PipelineState.HARD_FAIL,
            PipelineState.HALTED
        ]
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total execution duration."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class StateMachine:
    """
    Pipeline state machine for managing state transitions.
    Ensures deterministic and valid state transitions.
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        PipelineState.INIT: [PipelineState.RUNNING, PipelineState.CANCELLED],
        PipelineState.RUNNING: [
            PipelineState.PARTIAL_FAIL,
            PipelineState.COMPLETED,
            PipelineState.HARD_FAIL,
            PipelineState.CANCELLED
        ],
        PipelineState.PARTIAL_FAIL: [
            PipelineState.RETRY,
            PipelineState.HARD_FAIL,
            PipelineState.HALTED
        ],
        PipelineState.RETRY: [
            PipelineState.RUNNING,
            PipelineState.HARD_FAIL,
            PipelineState.HALTED
        ],
        PipelineState.HARD_FAIL: [],  # Terminal state
        PipelineState.HALTED: [],  # Terminal state
        PipelineState.COMPLETED: [],  # Terminal state
        PipelineState.CANCELLED: [],  # Terminal state
    }
    
    def __init__(self, execution_policy: ExecutionPolicy):
        self.policy = execution_policy
    
    def can_transition(self, current: PipelineState, next_state: PipelineState) -> bool:
        """Check if state transition is valid."""
        return next_state in self.VALID_TRANSITIONS.get(current, [])
    
    def transition(
        self,
        execution_state: PipelineExecutionState,
        next_state: PipelineState,
        reason: Optional[str] = None
    ) -> bool:
        """
        Attempt to transition pipeline to next state.
        
        Args:
            execution_state: Current execution state
            next_state: Target state
            reason: Optional reason for transition
            
        Returns:
            bool: True if transition successful, False otherwise
        """
        if not self.can_transition(execution_state.state, next_state):
            return False
        
        execution_state.state = next_state
        
        if next_state in [
            PipelineState.COMPLETED,
            PipelineState.HARD_FAIL,
            PipelineState.HALTED,
            PipelineState.CANCELLED
        ]:
            execution_state.end_time = datetime.utcnow()
        
        if reason:
            execution_state.error_message = reason
        
        return True
    
    def should_retry(
        self,
        execution_state: PipelineExecutionState,
        step_name: str
    ) -> bool:
        """
        Determine if a failed step should be retried.
        
        Args:
            execution_state: Current execution state
            step_name: Name of the failed step
            
        Returns:
            bool: True if retry should be attempted
        """
        step_metrics = execution_state.step_metrics.get(step_name)
        if not step_metrics:
            return True
        
        # Check step-level retry limit
        if step_metrics.retry_count >= self.policy.max_retries_per_step:
            return False
        
        # Check global failure limit
        if execution_state.total_failures >= self.policy.max_total_failures:
            return False
        
        # Check runtime limit
        if execution_state.start_time:
            runtime_minutes = (
                datetime.utcnow() - execution_state.start_time
            ).total_seconds() / 60
            if runtime_minutes >= self.policy.max_runtime_minutes:
                return False
        
        return True
    
    def should_halt(self, execution_state: PipelineExecutionState) -> bool:
        """
        Determine if pipeline should be halted.
        
        Args:
            execution_state: Current execution state
            
        Returns:
            bool: True if pipeline should halt
        """
        # Check global failure limit
        if execution_state.total_failures >= self.policy.max_total_failures:
            return True
        
        # Check runtime limit
        if execution_state.start_time:
            runtime_minutes = (
                datetime.utcnow() - execution_state.start_time
            ).total_seconds() / 60
            if runtime_minutes >= self.policy.max_runtime_minutes:
                return True
        
        return False
