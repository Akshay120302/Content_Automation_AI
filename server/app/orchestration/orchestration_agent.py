"""
Orchestration Agent - Central control plane for pipeline execution.
Manages DAG execution, state transitions, and agent coordination.
"""

from typing import Dict, Any, List, Optional, Set
import asyncio
from datetime import datetime
from pathlib import Path

from .dag import ExecutionDAG, DAGNode, DAGBuilder, NodeType
from .state_machine import (
    StateMachine,
    PipelineExecutionState,
    PipelineState,
    StepState,
    StepMetrics,
    ExecutionPolicy
)
from ..logging_system.pipeline_logger import PipelineLogger, EventType
from ..agents.research.deep_research_agent import DeepResearchAgent, ResearchDepth
from ..agents.content.content_agents import ScriptAgent, ImageAgent, AudioAgent, VideoAgent
from ..agents.quality.quality_check_agent import QualityCheckAgent, QCStatus
from ..agents.composer.composer_agent import ComposerAgent
from ..agents.base_agent import AgentInput, AgentStatus


class OrchestrationAgent:
    """
    Orchestration Agent - Central brain for pipeline execution.
    
    Responsibilities:
    - Load pipeline configuration
    - Build execution DAG
    - Dispatch jobs to agents
    - Track state transitions
    - Enforce retry/timeout policies
    - Emit structured logs
    - Handle failures
    
    This is a control plane, NOT a content generator.
    Acts as a deterministic state machine.
    """
    
    def __init__(
        self,
        execution_policy: Optional[ExecutionPolicy] = None,
        log_directory: Optional[Path] = None
    ):
        self.policy = execution_policy or ExecutionPolicy()
        self.log_directory = log_directory or Path("logs/pipelines")
        
        # Initialize state machine
        self.state_machine = StateMachine(self.policy)
        
        # Agent registry
        self.agents = {
            "DeepResearchAgent": DeepResearchAgent(),
            "ScriptAgent": ScriptAgent(),
            "ImageAgent": ImageAgent(),
            "AudioAgent": AudioAgent(),
            "VideoAgent": VideoAgent(),
            "QualityCheckAgent": QualityCheckAgent(),
            "ComposerAgent": ComposerAgent()
        }
    
    async def execute_pipeline(
        self,
        pipeline_id: str,
        pipeline_run_id: str,
        pipeline_config: Dict[str, Any],
        user_assets: Dict[str, Any]
    ) -> PipelineExecutionState:
        """
        Execute a complete pipeline.
        
        Args:
            pipeline_id: Pipeline identifier
            pipeline_run_id: Unique run identifier
            pipeline_config: Pipeline configuration
            user_assets: User-provided assets
            
        Returns:
            PipelineExecutionState with final state
        """
        # Initialize execution state
        execution_state = PipelineExecutionState(
            pipeline_run_id=pipeline_run_id,
            pipeline_id=pipeline_id,
            state=PipelineState.INIT,
            start_time=datetime.utcnow()
        )
        
        # Initialize logger
        log_file = self.log_directory / f"{pipeline_run_id}.log"
        logger = PipelineLogger(
            pipeline_run_id=pipeline_run_id,
            pipeline_id=pipeline_id,
            log_file=log_file
        )
        
        try:
            # Transition to RUNNING
            self.state_machine.transition(execution_state, PipelineState.RUNNING)
            logger.pipeline_started(pipeline_config)
            
            # Build execution DAG
            dag = DAGBuilder.build_standard_dag(pipeline_config, user_assets)
            logger.logger.info(f"Built execution DAG: {dag.get_execution_summary()}")
            
            # Execute DAG
            success = await self._execute_dag(
                dag=dag,
                execution_state=execution_state,
                pipeline_config=pipeline_config,
                user_assets=user_assets,
                logger=logger
            )
            
            # Final state transition
            if success:
                execution_state.state = PipelineState.COMPLETED
                execution_state.end_time = datetime.utcnow()
                duration_ms = execution_state.duration_seconds * 1000 if execution_state.duration_seconds else 0
                logger.pipeline_completed(duration_ms)
            else:
                execution_state.state = PipelineState.HARD_FAIL
                execution_state.end_time = datetime.utcnow()
                duration_ms = execution_state.duration_seconds * 1000 if execution_state.duration_seconds else 0
                logger.pipeline_failed(
                    execution_state.error_message or "Pipeline failed",
                    duration_ms
                )
            
        except Exception as e:
            # Unexpected error
            execution_state.state = PipelineState.HARD_FAIL
            execution_state.end_time = datetime.utcnow()
            execution_state.error_message = str(e)
            
            duration_ms = execution_state.duration_seconds * 1000 if execution_state.duration_seconds else 0
            logger.pipeline_failed(str(e), duration_ms)
        
        return execution_state
    
    async def _execute_dag(
        self,
        dag: ExecutionDAG,
        execution_state: PipelineExecutionState,
        pipeline_config: Dict[str, Any],
        user_assets: Dict[str, Any],
        logger: PipelineLogger
    ) -> bool:
        """
        Execute the DAG with parallel execution and dependency resolution.
        
        Returns:
            bool: True if all nodes executed successfully
        """
        completed_nodes: Set[str] = set()
        running_nodes: Set[str] = set()
        node_outputs: Dict[str, Any] = {}
        
        while True:
            # Check for halt conditions
            if self.state_machine.should_halt(execution_state):
                execution_state.error_message = "Pipeline halted: retry/failure/timeout limit reached"
                logger.logger.error(execution_state.error_message)
                return False
            
            # Get ready nodes
            ready_nodes = dag.get_ready_nodes(
                completed_nodes=completed_nodes,
                running_nodes=running_nodes,
                context=execution_state.context_data
            )
            
            # If no ready nodes and no running nodes, we're done
            if not ready_nodes and not running_nodes:
                break
            
            # If no ready nodes but have running nodes, wait
            if not ready_nodes and running_nodes:
                await asyncio.sleep(0.5)
                continue
            
            # Execute ready nodes in parallel (if enabled)
            if self.policy.enable_parallel_execution:
                parallel_groups = dag.get_parallel_groups(ready_nodes)
                
                for group_name, group_nodes in parallel_groups.items():
                    # Execute group in parallel
                    tasks = []
                    for node in group_nodes:
                        running_nodes.add(node.node_id)
                        task = self._execute_node(
                            node=node,
                            execution_state=execution_state,
                            pipeline_config=pipeline_config,
                            user_assets=user_assets,
                            node_outputs=node_outputs,
                            logger=logger
                        )
                        tasks.append(task)
                    
                    # Wait for group to complete
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    for node, result in zip(group_nodes, results):
                        running_nodes.remove(node.node_id)
                        
                        if isinstance(result, Exception):
                            # Node failed
                            execution_state.total_failures += 1
                            logger.logger.error(f"Node {node.node_id} failed: {result}")
                            
                            # Check if should retry
                            if not self.state_machine.should_retry(execution_state, node.node_id):
                                if node.required:
                                    execution_state.error_message = f"Required node {node.node_id} failed"
                                    return False
                            else:
                                # Retry node
                                logger.step_retry(
                                    node.node_id,
                                    node.agent_name,
                                    execution_state.step_metrics[node.node_id].retry_count
                                )
                                # Node will be retried in next iteration
                        else:
                            # Node succeeded
                            completed_nodes.add(node.node_id)
                            node_outputs[node.node_id] = result
                            
                            # Special handling for QC node
                            if node.node_type == NodeType.QUALITY_CHECK:
                                qc_result = result.get("qc_result", {})
                                if qc_result.get("status") == "HARD_FAIL":
                                    execution_state.error_message = "Quality check hard fail"
                                    return False
                                elif qc_result.get("status") == "SOFT_FAIL":
                                    # Regenerate specific step
                                    next_action = result.get("next_action")
                                    logger.logger.warning(f"QC soft fail: {next_action}")
                                    # TODO: Implement regeneration logic
            else:
                # Sequential execution
                for node in ready_nodes:
                    running_nodes.add(node.node_id)
                    
                    try:
                        result = await self._execute_node(
                            node=node,
                            execution_state=execution_state,
                            pipeline_config=pipeline_config,
                            user_assets=user_assets,
                            node_outputs=node_outputs,
                            logger=logger
                        )
                        
                        running_nodes.remove(node.node_id)
                        completed_nodes.add(node.node_id)
                        node_outputs[node.node_id] = result
                        
                    except Exception as e:
                        running_nodes.remove(node.node_id)
                        execution_state.total_failures += 1
                        
                        if not self.state_machine.should_retry(execution_state, node.node_id):
                            if node.required:
                                execution_state.error_message = f"Required node {node.node_id} failed: {e}"
                                return False
        
        # Check if all required nodes completed
        required_nodes = [n.node_id for n in dag.nodes.values() if n.required]
        missing_required = [n for n in required_nodes if n not in completed_nodes]
        
        if missing_required:
            execution_state.error_message = f"Required nodes not completed: {missing_required}"
            return False
        
        # Store final outputs in execution state
        execution_state.context_data["final_outputs"] = node_outputs
        
        return True
    
    async def _execute_node(
        self,
        node: DAGNode,
        execution_state: PipelineExecutionState,
        pipeline_config: Dict[str, Any],
        user_assets: Dict[str, Any],
        node_outputs: Dict[str, Any],
        logger: PipelineLogger
    ) -> Dict[str, Any]:
        """
        Execute a single DAG node.
        
        Returns:
            Dict with node output data
        """
        # Initialize step metrics
        if node.node_id not in execution_state.step_metrics:
            execution_state.step_metrics[node.node_id] = StepMetrics(
                step_name=node.node_id,
                agent_name=node.agent_name,
                state=StepState.PENDING
            )
        
        step_metrics = execution_state.step_metrics[node.node_id]
        step_metrics.state = StepState.START
        step_metrics.start_time = datetime.utcnow()
        step_metrics.retry_count += 1
        
        execution_state.current_step = node.node_id
        
        logger.step_start(node.node_id, node.agent_name)
        
        try:
            # Get agent
            agent = self.agents.get(node.agent_name)
            if not agent:
                raise ValueError(f"Agent {node.agent_name} not found")
            
            # Prepare agent input
            agent_input = AgentInput(
                pipeline_config=pipeline_config,
                context_pack=execution_state.context_data.get("context_pack"),
                user_assets=user_assets,
                previous_outputs=node_outputs,
                metadata=node.metadata
            )
            
            # Execute agent with timeout
            output = await asyncio.wait_for(
                agent.execute(agent_input),
                timeout=node.timeout_seconds
            )
            
            # Check output status
            if output.status != AgentStatus.SUCCESS:
                raise RuntimeError(f"Agent failed: {output.error}")
            
            # Update metrics
            step_metrics.state = StepState.SUCCESS
            step_metrics.end_time = datetime.utcnow()
            step_metrics.payload_summary = output.to_dict()
            
            duration_ms = step_metrics.duration_seconds * 1000 if step_metrics.duration_seconds else 0
            logger.step_success(
                node.node_id,
                node.agent_name,
                duration_ms,
                output.output_data
            )
            
            # Store context for downstream nodes
            if node.node_type == NodeType.RESEARCH:
                execution_state.context_data["context_pack"] = output.output_data
            
            return output.output_data
            
        except asyncio.TimeoutError:
            step_metrics.state = StepState.TIMEOUT
            step_metrics.end_time = datetime.utcnow()
            step_metrics.error_message = f"Timeout after {node.timeout_seconds}s"
            
            logger.step_fail(
                node.node_id,
                node.agent_name,
                step_metrics.error_message,
                step_metrics.retry_count
            )
            
            raise
            
        except Exception as e:
            step_metrics.state = StepState.FAIL
            step_metrics.end_time = datetime.utcnow()
            step_metrics.error_message = str(e)
            
            logger.step_fail(
                node.node_id,
                node.agent_name,
                str(e),
                step_metrics.retry_count
            )
            
            raise
    
    def get_execution_status(
        self,
        execution_state: PipelineExecutionState
    ) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            "pipeline_run_id": execution_state.pipeline_run_id,
            "pipeline_id": execution_state.pipeline_id,
            "state": execution_state.state.value,
            "current_step": execution_state.current_step,
            "total_failures": execution_state.total_failures,
            "start_time": execution_state.start_time.isoformat() if execution_state.start_time else None,
            "duration_seconds": execution_state.duration_seconds,
            "is_terminal": execution_state.is_terminal,
            "is_failed": execution_state.is_failed,
            "steps": {
                step_name: {
                    "state": metrics.state.value,
                    "retry_count": metrics.retry_count,
                    "duration_seconds": metrics.duration_seconds,
                    "error": metrics.error_message
                }
                for step_name, metrics in execution_state.step_metrics.items()
            }
        }
