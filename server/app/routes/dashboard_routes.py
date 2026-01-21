from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.routes.auth_routes import get_authenticated_user
from app.schemas.pipeline_schema import PipelineResponse
from app.controllers.dashboard_controller import get_user_pipelines, get_pipeline_by_id


# Define the router
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=List[PipelineResponse], status_code=status.HTTP_200_OK)
def get_dashboard_pipelines(
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Get all pipelines for the authenticated user
    
    Returns:
        List of user's pipelines
    """
    return get_user_pipelines(current_user.id, db)


@router.get("/{pipeline_id}", response_model=PipelineResponse, status_code=status.HTTP_200_OK)
def get_pipeline_details(
    pipeline_id: int,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific pipeline
    
    Args:
        pipeline_id: The ID of the pipeline
        
    Returns:
        Pipeline details
    """
    return get_pipeline_by_id(pipeline_id, current_user.id, db)
