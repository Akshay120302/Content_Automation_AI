from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models.pipeline import Pipeline
from app.schemas.pipeline_schema import PipelineCreate, PipelineResponse


# Create a new pipeline for a user
def create_pipeline(pipeline_data: PipelineCreate, user_id: UUID, db: Session) -> PipelineResponse:
    """
    Create a new content automation pipeline for a user
    
    Args:
        pipeline_data: Pipeline creation data from the request
        user_id: The UUID of the authenticated user
        db: Database session
        
    Returns:
        Created pipeline response
    """
    try:
        # Create new pipeline instance
        new_pipeline = Pipeline(
            user_id=user_id,
            platform=pipeline_data.platform,
            content_type=pipeline_data.content_type,
            agent_model=pipeline_data.agent_model,
            manual_review=pipeline_data.manual_review,
            additional_prompt=pipeline_data.additional_prompt,
            posting_time=pipeline_data.posting_time,
            timezone=pipeline_data.timezone,
            frequency=pipeline_data.frequency,
            times_per_week=pipeline_data.times_per_week,
            temperature=pipeline_data.temperature,
            connected_accounts=pipeline_data.connected_accounts,
            genre=pipeline_data.genre,
            topic_type=pipeline_data.topic_type,
            topic_value=pipeline_data.topic_value,
            target_regions=pipeline_data.target_regions
        )
        
        # Add to database
        db.add(new_pipeline)
        db.commit()
        db.refresh(new_pipeline)
        
        return PipelineResponse.from_orm(new_pipeline)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pipeline: {str(e)}"
        )


# Update an existing pipeline
def update_pipeline(pipeline_id: int, pipeline_data: PipelineCreate, user_id: UUID, db: Session) -> PipelineResponse:
    """
    Update an existing pipeline
    
    Args:
        pipeline_id: The ID of the pipeline to update
        pipeline_data: Updated pipeline data
        user_id: The UUID of the authenticated user
        db: Database session
        
    Returns:
        Updated pipeline response
    """
    # Find the pipeline
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.user_id == user_id
    ).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found or you don't have permission to update it"
        )
    
    try:
        # Update fields
        pipeline.platform = pipeline_data.platform
        pipeline.content_type = pipeline_data.content_type
        pipeline.agent_model = pipeline_data.agent_model
        pipeline.manual_review = pipeline_data.manual_review
        pipeline.additional_prompt = pipeline_data.additional_prompt
        pipeline.posting_time = pipeline_data.posting_time
        pipeline.timezone = pipeline_data.timezone
        pipeline.frequency = pipeline_data.frequency
        pipeline.times_per_week = pipeline_data.times_per_week
        pipeline.temperature = pipeline_data.temperature
        pipeline.connected_accounts = pipeline_data.connected_accounts
        pipeline.genre = pipeline_data.genre
        pipeline.topic_type = pipeline_data.topic_type
        pipeline.topic_value = pipeline_data.topic_value
        pipeline.target_regions = pipeline_data.target_regions
        
        db.commit()
        db.refresh(pipeline)
        
        return PipelineResponse.from_orm(pipeline)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pipeline: {str(e)}"
        )


# Delete a pipeline
def delete_pipeline(pipeline_id: int, user_id: UUID, db: Session) -> dict:
    """
    Delete a pipeline
    
    Args:
        pipeline_id: The ID of the pipeline to delete
        user_id: The UUID of the authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # Find the pipeline
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.user_id == user_id
    ).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found or you don't have permission to delete it"
        )
    
    try:
        db.delete(pipeline)
        db.commit()
        
        return {"message": "Pipeline deleted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete pipeline: {str(e)}"
        )
