from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from uuid import UUID

from app.models.pipeline import Pipeline
from app.schemas.pipeline_schema import PipelineResponse

# Get all pipelines for a user with user_id
def get_user_pipelines(user_id: UUID, db: Session) -> List[PipelineResponse]:
    """
    Get all pipelines created by a specific user
    
    Args:
        user_id: The UUID of the user
        db: Database session
        
    Returns:
        List of pipeline responses
    """
    try:
        # Query all pipelines for the user
        pipelines = db.query(Pipeline).filter(Pipeline.user_id == user_id).all()
        
        # Convert to response models
        return [PipelineResponse.from_orm(pipeline) for pipeline in pipelines]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pipelines: {str(e)}"
        )


# Get a specific pipeline by ID for a user
def get_pipeline_by_id(pipeline_id: int, user_id: UUID, db: Session) -> PipelineResponse:
    """
    Get a specific pipeline by ID for a user
    
    Args:
        pipeline_id: The ID of the pipeline
        user_id: The UUID of the user (for ownership verification)
        db: Database session
        
    Returns:
        Pipeline response
    """
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.user_id == user_id
    ).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found or you don't have permission to access it"
        )
    
    return PipelineResponse.from_orm(pipeline)
