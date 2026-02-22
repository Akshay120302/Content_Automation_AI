"""Base agent interface for all content generation agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


@dataclass
class AgentInput:
    """Standard input for all agents."""
    pipeline_config: Dict[str, Any]
    context_pack: Optional[Dict[str, Any]] = None
    user_assets: Optional[Dict[str, Any]] = None
    previous_outputs: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentOutput:
    """Standard output from all agents."""
    agent_name: str
    status: AgentStatus
    timestamp: datetime
    output_data: Dict[str, Any]
    artifacts: Dict[str, str] = None  # file_type -> file_path
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "output_data": self.output_data,
            "artifacts": self.artifacts or {},
            "metrics": self.metrics,
            "error": self.error
        }


class BaseAgent(ABC):
    """
    Base class for all agents.
    
    Design principles:
    - Stateless: No shared memory between executions
    - Idempotent: Same input = same output
    - Retryable: Can be safely retried on failure
    - No orchestration logic: Pure execution workers
    """
    
    def __init__(self, agent_name: str, timeout_seconds: int = 300):
        self.agent_name = agent_name
        self.timeout_seconds = timeout_seconds
    
    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute agent logic.
        
        Args:
            input_data: Standard agent input
            
        Returns:
            AgentOutput with results
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: AgentInput) -> bool:
        """
        Validate input before execution.
        
        Args:
            input_data: Input to validate
            
        Returns:
            bool: True if valid
        """
        pass
    
    def _create_output(
        self,
        status: AgentStatus,
        output_data: Dict[str, Any],
        artifacts: Optional[Dict[str, str]] = None,
        error: Optional[str] = None
    ) -> AgentOutput:
        """Helper to create standard output."""
        return AgentOutput(
            agent_name=self.agent_name,
            status=status,
            timestamp=datetime.utcnow(),
            output_data=output_data,
            artifacts=artifacts,
            error=error
        )
