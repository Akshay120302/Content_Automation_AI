"""
Integration example for connecting the agentic system to your existing API.
Add these endpoints to your pipeline_routes.py
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.database import get_db
from app.models.execution import PipelineRun, PipelineRunState, PipelineEvent
from app.models.pipeline import Pipeline
from app.models.user import User
from app.celery_config.pipeline_tasks import execute_pipeline, cancel_pipeline
from app.routes.auth_routes import get_authenticated_user  # Your existing auth dependency

router = APIRouter(prefix="/api/pipelines", tags=["Pipeline Execution"])


class ExecutePipelineRequest(BaseModel):
    """Optional overrides for pipeline execution"""
    user_assets: Optional[Dict[str, Any]] = None
    config_overrides: Optional[Dict[str, Any]] = None


@router.post("/{pipeline_id}/execute")
async def execute_pipeline_endpoint(
    pipeline_id: int,
    request_body: Optional[ExecutePipelineRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    Queue a pipeline for execution.
    
    Args:
        pipeline_id: ID of the pipeline to execute
        request_body: Optional user assets and config overrides
    
    Returns:
        - run_id: Unique execution ID
        - task_id: Celery task ID
        - status: Initial status (QUEUED)
    """
    # Verify pipeline exists and belongs to user
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.user_id == current_user.id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    # Generate run ID
    run_id = f"run_{pipeline_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    
    # Build pipeline config from database record
    pipeline_config = {
        "pipeline_id": pipeline.id,
        "run_id": run_id,
        "user_id": str(current_user.id),
        "platform": pipeline.platform.value if hasattr(pipeline.platform, 'value') else pipeline.platform,
        "content_type": pipeline.content_type.value if hasattr(pipeline.content_type, 'value') else pipeline.content_type,
        "agent_model": pipeline.agent_model.value if hasattr(pipeline.agent_model, 'value') else pipeline.agent_model,
        "tone": pipeline.genre.value if hasattr(pipeline.genre, 'value') else pipeline.genre,
        "topic_type": pipeline.topic_type.value if hasattr(pipeline.topic_type, 'value') else pipeline.topic_type,
        "topic": pipeline.topic_value,
        "additional_prompt": pipeline.additional_prompt,
        "temperature": pipeline.temperature,
        "manual_review": pipeline.manual_review,
        "llm_model": pipeline.agent_model.value if hasattr(pipeline.agent_model, 'value') else pipeline.agent_model,
        "llm_provider": "openai" if "gpt" in str(pipeline.agent_model).lower() else "anthropic",
        "video_provider": pipeline.video_provider,
        "video_model": pipeline.video_model,
        "video_duration_seconds": pipeline.video_duration_seconds,
        "video_aspect_ratio": pipeline.video_aspect_ratio,
        "video_fps": pipeline.video_fps
    }
    
    # Apply config overrides if provided
    if request_body and request_body.config_overrides:
        pipeline_config.update(request_body.config_overrides)
    
    # Get user assets
    user_assets = request_body.user_assets if request_body else {}
    
    # Create pipeline run record
    pipeline_run = PipelineRun(
        run_id=run_id,
        pipeline_id=pipeline_id,
        user_id=current_user.id,
        state=PipelineRunState.QUEUED,
        config_snapshot=pipeline_config,
        created_at=datetime.utcnow()
    )
    db.add(pipeline_run)
    db.commit()
    
    # Queue pipeline execution via Celery
    task = execute_pipeline.delay(
        pipeline_id=str(pipeline_id),
        pipeline_run_id=run_id,
        pipeline_config=pipeline_config,
        user_assets=user_assets
    )
    
    # Update with Celery task ID
    pipeline_run.celery_task_id = task.id
    db.commit()
    
    return {
        "run_id": run_id,
        "task_id": task.id,
        "status": "queued",
        "message": "Pipeline execution queued successfully"
    }


@router.get("/runs/{run_id}")
async def get_pipeline_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    Get pipeline run status and details.
    """
    run = db.query(PipelineRun).filter(
        PipelineRun.run_id == run_id,
        PipelineRun.user_id == current_user.id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    # Get step details
    steps = [step.to_dict() for step in run.steps]
    
    # Calculate progress
    total_steps = len(steps)
    completed_steps = len([s for s in steps if s["state"] == "SUCCESS"])
    progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
    
    return {
        **run.to_dict(),
        "steps": steps,
        "progress_percent": progress,
        "is_running": run.state == PipelineRunState.RUNNING,
        "is_complete": run.state == PipelineRunState.COMPLETED,
        "is_failed": run.state in [
            PipelineRunState.HARD_FAIL,
            PipelineRunState.HALTED
        ]
    }


@router.get("/runs/{run_id}/logs")
async def get_pipeline_logs(
    run_id: str,
    event_type: str = None,
    level: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    Get pipeline execution logs (events).
    
    Query params:
        - event_type: Filter by event type
        - level: Filter by log level (INFO, WARNING, ERROR)
        - limit: Max events to return
    """
    # Verify access
    run = db.query(PipelineRun).filter(
        PipelineRun.run_id == run_id,
        PipelineRun.user_id == current_user.id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    # Build query
    query = db.query(PipelineEvent).filter(PipelineEvent.run_id == run_id)
    
    if event_type:
        query = query.filter(PipelineEvent.event_type == event_type)
    
    if level:
        query = query.filter(PipelineEvent.level == level)
    
    # Order by timestamp and limit
    events = query.order_by(PipelineEvent.timestamp).limit(limit).all()
    
    return {
        "run_id": run_id,
        "total_events": len(events),
        "events": [event.to_dict() for event in events]
    }


@router.post("/runs/{run_id}/cancel")
async def cancel_pipeline_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    Cancel a running pipeline.
    """
    # Verify access
    run = db.query(PipelineRun).filter(
        PipelineRun.run_id == run_id,
        PipelineRun.user_id == current_user.id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    # Check if cancellable
    if run.state not in [PipelineRunState.QUEUED, PipelineRunState.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel pipeline in {run.state.value} state"
        )
    
    # Send cancellation task
    cancel_pipeline.delay(run_id)
    
    # Update state
    run.state = PipelineRunState.CANCELLED
    run.completed_at = datetime.utcnow()
    db.commit()
    
    return {
        "run_id": run_id,
        "status": "cancelled",
        "message": "Pipeline cancellation initiated"
    }


@router.get("/runs")
async def list_pipeline_runs(
    pipeline_id: int = None,
    state: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    List pipeline runs for the current user.
    
    Query params:
        - pipeline_id: Filter by pipeline
        - state: Filter by state (RUNNING, COMPLETED, FAILED, etc.)
        - limit: Results per page
        - offset: Pagination offset
    """
    query = db.query(PipelineRun).filter(
        PipelineRun.user_id == current_user.id
    )
    
    if pipeline_id is not None:
        query = query.filter(PipelineRun.pipeline_id == pipeline_id)
    
    if state:
        query = query.filter(PipelineRun.state == state)
    
    # Order by created_at desc
    total = query.count()
    runs = query.order_by(
        PipelineRun.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "runs": [run.to_dict() for run in runs]
    }


@router.get("/runs/{run_id}/outputs")
async def get_pipeline_outputs(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    Get final outputs from a completed pipeline.
    
    Returns:
        - final_video_url
        - script
        - images
        - audio
        - metadata
    """
    run = db.query(PipelineRun).filter(
        PipelineRun.run_id == run_id,
        PipelineRun.user_id == current_user.id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    if run.state != PipelineRunState.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline not completed (state: {run.state.value})"
        )
    
    return {
        "run_id": run_id,
        "outputs": run.outputs or {},
        "artifacts": run.artifacts or {},
        "run_metadata": run.run_metadata or {}
    }


@router.post("/runs/{run_id}/retry")
async def retry_pipeline_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    Retry a failed pipeline with same configuration.
    """
    # Get original run
    original_run = db.query(PipelineRun).filter(
        PipelineRun.run_id == run_id,
        PipelineRun.user_id == current_user.id
    ).first()
    
    if not original_run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    # Check if retry is valid
    if original_run.state not in [
        PipelineRunState.HARD_FAIL,
        PipelineRunState.HALTED
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry pipeline in {original_run.state.value} state"
        )
    
    # Create new run
    new_run_id = f"{run_id}_retry_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    new_run = PipelineRun(
        run_id=new_run_id,
        pipeline_id=original_run.pipeline_id,
        user_id=current_user.id,
        state=PipelineRunState.QUEUED,
        config_snapshot=original_run.config_snapshot,
        user_assets=original_run.user_assets,
        created_at=datetime.utcnow(),
        metadata={"retried_from": run_id}
    )
    db.add(new_run)
    db.commit()
    
    # Queue execution
    task = execute_pipeline.delay(
        pipeline_id=original_run.pipeline_id,
        pipeline_run_id=new_run_id,
        pipeline_config=original_run.config_snapshot,
        user_assets=original_run.user_assets or {}
    )
    
    new_run.celery_task_id = task.id
    db.commit()
    
    return {
        "original_run_id": run_id,
        "new_run_id": new_run_id,
        "task_id": task.id,
        "status": "queued",
        "message": "Pipeline retry queued successfully"
    }


@router.get("/stats")
async def get_execution_stats(
    pipeline_id: int = None,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """
    Get execution statistics for user's pipelines.
    
    Returns:
        - Total executions
        - Success rate
        - Average duration
        - Failure breakdown
    """
    from datetime import timedelta
    from sqlalchemy import func
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(PipelineRun).filter(
        PipelineRun.user_id == current_user.id,
        PipelineRun.created_at >= cutoff
    )
    
    if pipeline_id is not None:
        query = query.filter(PipelineRun.pipeline_id == pipeline_id)
    
    total = query.count()
    completed = query.filter(
        PipelineRun.state == PipelineRunState.COMPLETED
    ).count()
    failed = query.filter(
        PipelineRun.state.in_([
            PipelineRunState.HARD_FAIL,
            PipelineRunState.HALTED
        ])
    ).count()
    
    # Average duration for completed runs
    avg_duration = db.query(
        func.avg(PipelineRun.duration_seconds)
    ).filter(
        PipelineRun.user_id == current_user.id,
        PipelineRun.state == PipelineRunState.COMPLETED,
        PipelineRun.created_at >= cutoff
    ).scalar() or 0
    
    return {
        "period_days": days,
        "total_executions": total,
        "completed": completed,
        "failed": failed,
        "running": total - completed - failed,
        "success_rate": (completed / total * 100) if total > 0 else 0,
        "average_duration_seconds": float(avg_duration),
        "failure_rate": (failed / total * 100) if total > 0 else 0
    }
