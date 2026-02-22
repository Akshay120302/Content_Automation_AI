"""
Pipeline tasks for Celery.
Main entry point for pipeline execution via job queue.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime
import logging
from uuid import uuid4

from .celery_app import celery_app, pipeline_task, TaskPriority
from ..orchestration.orchestration_agent import OrchestrationAgent
from ..orchestration.state_machine import ExecutionPolicy
from ..database.database import SessionLocal
from ..models.execution import (
    PipelineRun,
    PipelineRunState,
    PipelineRunStep,
    PipelineEvent,
    StepState as DbStepState,
    EventType as DbEventType,
    LogLevel as DbLogLevel
)

logger = logging.getLogger(__name__)


@pipeline_task(
    name='execute_pipeline',
    priority=TaskPriority.HIGH
)
def execute_pipeline(
    self,
    pipeline_id: str,
    pipeline_run_id: str,
    pipeline_config: Dict[str, Any],
    user_assets: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a complete content generation pipeline.
    
    This is the main entry point for pipeline execution.
    Called by the scheduler or API endpoint.
    
    Args:
        pipeline_id: Pipeline identifier
        pipeline_run_id: Unique run identifier
        pipeline_config: Pipeline configuration
        user_assets: User-provided assets
        
    Returns:
        Dict with execution results and final state
    """
    logger.info(f"Starting pipeline execution: {pipeline_run_id}")
    
    db = SessionLocal()
    try:
        # Mark run as RUNNING
        run = db.query(PipelineRun).filter(PipelineRun.run_id == pipeline_run_id).first()
        if run:
            run.state = PipelineRunState.RUNNING
            run.started_at = datetime.utcnow()
            run.current_step = None
            run.user_assets = user_assets
            run.execution_policy = {
                "max_retries_per_step": 2,
                "max_total_failures": 5,
                "max_runtime_minutes": 30,
                "enable_parallel_execution": True
            }
            db.commit()

        # Create orchestration agent
        policy = ExecutionPolicy(
            max_retries_per_step=2,
            max_total_failures=5,
            max_runtime_minutes=30,
            enable_parallel_execution=True
        )
        
        orchestrator = OrchestrationAgent(execution_policy=policy)
        
        # Execute pipeline (sync wrapper for async function)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        execution_state = loop.run_until_complete(
            orchestrator.execute_pipeline(
                pipeline_id=pipeline_id,
                pipeline_run_id=pipeline_run_id,
                pipeline_config=pipeline_config,
                user_assets=user_assets
            )
        )
        
        # Get execution status
        status = orchestrator.get_execution_status(execution_state)

        # Persist run, steps, and events
        run = db.query(PipelineRun).filter(PipelineRun.run_id == pipeline_run_id).first()
        if run:
            state_value = execution_state.state.value
            run.state = PipelineRunState[state_value] if state_value in PipelineRunState.__members__ else PipelineRunState.HARD_FAIL
            run.current_step = execution_state.current_step
            run.completed_at = execution_state.end_time
            run.duration_seconds = execution_state.duration_seconds
            run.total_failures = execution_state.total_failures
            run.error_message = execution_state.error_message
            run.outputs = execution_state.context_data.get("final_outputs", {})
            run.run_metadata = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            db.commit()

        # Upsert step metrics
        for step_name, metrics in execution_state.step_metrics.items():
            step = (
                db.query(PipelineRunStep)
                .filter(PipelineRunStep.run_id == pipeline_run_id, PipelineRunStep.step_name == step_name)
                .first()
            )
            if not step:
                step = PipelineRunStep(
                    run_id=pipeline_run_id,
                    step_name=step_name,
                    agent_name=metrics.agent_name
                )
                db.add(step)

            step.state = DbStepState[metrics.state.value] if metrics.state.value in DbStepState.__members__ else DbStepState.FAIL
            step.started_at = metrics.start_time
            step.completed_at = metrics.end_time
            step.duration_seconds = metrics.duration_seconds
            step.retry_count = metrics.retry_count
            step.error_message = metrics.error_message
            step.output_summary = metrics.payload_summary
        db.commit()

        # Insert high-level events
        events = []
        if execution_state.start_time:
            events.append(PipelineEvent(
                event_id=str(uuid4()),
                run_id=pipeline_run_id,
                pipeline_id=str(pipeline_id),
                timestamp=execution_state.start_time,
                event_type=DbEventType.PIPELINE_STARTED,
                level=DbLogLevel.INFO,
                message="Pipeline execution started"
            ))

        for step_name, metrics in execution_state.step_metrics.items():
            if metrics.start_time:
                events.append(PipelineEvent(
                    event_id=str(uuid4()),
                    run_id=pipeline_run_id,
                    pipeline_id=str(pipeline_id),
                    timestamp=metrics.start_time,
                    event_type=DbEventType.STEP_START,
                    level=DbLogLevel.INFO,
                    step_name=step_name,
                    agent_name=metrics.agent_name,
                    message=f"Step {step_name} started"
                ))
            if metrics.end_time:
                end_event_type = DbEventType.STEP_SUCCESS if metrics.state.value == "SUCCESS" else DbEventType.STEP_FAIL
                end_level = DbLogLevel.INFO if metrics.state.value == "SUCCESS" else DbLogLevel.ERROR
                events.append(PipelineEvent(
                    event_id=str(uuid4()),
                    run_id=pipeline_run_id,
                    pipeline_id=str(pipeline_id),
                    timestamp=metrics.end_time,
                    event_type=end_event_type,
                    level=end_level,
                    step_name=step_name,
                    agent_name=metrics.agent_name,
                    message=f"Step {step_name} finished",
                    error=metrics.error_message,
                    duration_ms=(metrics.duration_seconds * 1000) if metrics.duration_seconds else None,
                    retry_count=metrics.retry_count
                ))

        if execution_state.end_time:
            events.append(PipelineEvent(
                event_id=str(uuid4()),
                run_id=pipeline_run_id,
                pipeline_id=str(pipeline_id),
                timestamp=execution_state.end_time,
                event_type=DbEventType.PIPELINE_COMPLETED if not execution_state.is_failed else DbEventType.PIPELINE_FAILED,
                level=DbLogLevel.INFO if not execution_state.is_failed else DbLogLevel.ERROR,
                message="Pipeline completed" if not execution_state.is_failed else "Pipeline failed",
                error=execution_state.error_message,
                duration_ms=(execution_state.duration_seconds * 1000) if execution_state.duration_seconds else None
            ))

        if events:
            db.add_all(events)
            db.commit()
        
        logger.info(
            f"Pipeline execution completed: {pipeline_run_id} - "
            f"State: {execution_state.state.value}"
        )
        
        # TODO: Update database with final state
        # This would call your pipeline controller to update status
        
        return {
            "success": not execution_state.is_failed,
            "pipeline_run_id": pipeline_run_id,
            "state": execution_state.state.value,
            "status": status,
            "outputs": execution_state.context_data.get("final_outputs", {}),
            "error": execution_state.error_message
        }
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {pipeline_run_id} - {str(e)}")

        # Update database with error state
        try:
            run = db.query(PipelineRun).filter(PipelineRun.run_id == pipeline_run_id).first()
            if run:
                run.state = PipelineRunState.HARD_FAIL
                run.completed_at = datetime.utcnow()
                run.error_message = str(e)
                run.total_failures = (run.total_failures or 0) + 1
                db.commit()
        except Exception:
            db.rollback()

        return {
            "success": False,
            "pipeline_run_id": pipeline_run_id,
            "state": "HARD_FAIL",
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(
    name='execute_pipeline_async',
    bind=True,
    priority=TaskPriority.HIGH
)
def execute_pipeline_async(
    self,
    pipeline_id: str,
    pipeline_run_id: str,
    pipeline_config: Dict[str, Any],
    user_assets: Dict[str, Any]
):
    """
    Async variant of pipeline execution.
    Useful for long-running pipelines.
    """
    return execute_pipeline(
        self,
        pipeline_id=pipeline_id,
        pipeline_run_id=pipeline_run_id,
        pipeline_config=pipeline_config,
        user_assets=user_assets
    )


@celery_app.task(
    name='retry_failed_pipeline',
    bind=True,
    priority=TaskPriority.NORMAL
)
def retry_failed_pipeline(
    self,
    pipeline_id: str,
    original_run_id: str,
    pipeline_config: Dict[str, Any],
    user_assets: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Retry a failed pipeline execution.
    
    Creates a new run with same config.
    """
    # Generate new run ID
    new_run_id = f"{original_run_id}_retry_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    logger.info(f"Retrying pipeline {original_run_id} as {new_run_id}")
    
    return execute_pipeline(
        self,
        pipeline_id=pipeline_id,
        pipeline_run_id=new_run_id,
        pipeline_config=pipeline_config,
        user_assets=user_assets
    )


@celery_app.task(
    name='cancel_pipeline',
    bind=True,
    priority=TaskPriority.CRITICAL
)
def cancel_pipeline(self, pipeline_run_id: str) -> Dict[str, Any]:
    """
    Cancel a running pipeline.
    
    Sends cancellation signal to orchestrator.
    """
    logger.info(f"Cancelling pipeline: {pipeline_run_id}")
    
    try:
        # TODO: Implement cancellation logic
        # This would involve:
        # 1. Checking if pipeline is still running
        # 2. Sending cancellation signal
        # 3. Cleaning up resources
        # 4. Updating database state
        return {
            "success": True,
            "pipeline_run_id": pipeline_run_id,
            "status": "cancel_requested"
        }
    except Exception as e:
        logger.error(f"Failed to cancel pipeline {pipeline_run_id}: {str(e)}")
        return {
            "success": False,
            "pipeline_run_id": pipeline_run_id,
            "error": str(e)
        }


@celery_app.task(
    name='get_pipeline_status',
    bind=True,
    priority=TaskPriority.NORMAL
)
def get_pipeline_status(self, pipeline_run_id: str) -> Dict[str, Any]:
    """
    Get current status of a running pipeline.
    
    Queries the execution state from database/cache.
    """
    try:
        # TODO: Query execution state from database
        # This would retrieve the latest state from your pipeline_runs table
        
        return {
            "pipeline_run_id": pipeline_run_id,
            "state": "RUNNING",  # Placeholder
            "current_step": "script",  # Placeholder
            "progress_percent": 0.5  # Placeholder
        }
        
    except Exception as e:
        logger.error(f"Failed to get pipeline status {pipeline_run_id}: {str(e)}")
        return {
            "pipeline_run_id": pipeline_run_id,
            "error": str(e)
        }


@celery_app.task(
    name='batch_execute_pipelines',
    bind=True,
    priority=TaskPriority.LOW
)
def batch_execute_pipelines(
    self,
    pipelines: list[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Execute multiple pipelines in batch.
    
    Useful for scheduled content generation.
    
    Args:
        pipelines: List of pipeline configurations
        
    Returns:
        Dict with batch execution results
    """
    logger.info(f"Starting batch execution of {len(pipelines)} pipelines")
    
    results = []
    
    for idx, pipeline_data in enumerate(pipelines):
        try:
            # Queue each pipeline
            task = execute_pipeline.delay(
                pipeline_id=pipeline_data["pipeline_id"],
                pipeline_run_id=pipeline_data["pipeline_run_id"],
                pipeline_config=pipeline_data["config"],
                user_assets=pipeline_data.get("assets", {})
            )
            
            results.append({
                "pipeline_id": pipeline_data["pipeline_id"],
                "task_id": task.id,
                "status": "queued"
            })
            
        except Exception as e:
            logger.error(f"Failed to queue pipeline {idx}: {str(e)}")
            results.append({
                "pipeline_id": pipeline_data.get("pipeline_id"),
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "total": len(pipelines),
        "queued": len([r for r in results if r["status"] == "queued"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }
