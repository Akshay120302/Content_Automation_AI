from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.routes.auth_routes import get_authenticated_user
from app.schemas.pipeline_schema import PipelineCreate, PipelineResponse
from app.controllers.pipeline_controller import create_pipeline, update_pipeline, delete_pipeline, get_user_pipelines, get_pipeline_by_id


# Define the router
router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("", response_model=List[PipelineResponse], status_code=status.HTTP_200_OK)
def get_all_pipelines(
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
def get_pipeline(
    pipeline_id: int,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific pipeline by ID
    
    Args:
        pipeline_id: The ID of the pipeline to retrieve
        
    Returns:
        Pipeline details
    """
    return get_pipeline_by_id(pipeline_id, current_user.id, db)


@router.post("", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
def create_new_pipeline(
    pipeline_data: PipelineCreate,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Create a new content automation pipeline
    
    This endpoint is called when the user submits the create pipeline modal form.
    
    Args:
        pipeline_data: Pipeline configuration data from the modal form
        
    Returns:
        Created pipeline details
    """
    return create_pipeline(pipeline_data, current_user.id, db)


@router.put("/{pipeline_id}", response_model=PipelineResponse, status_code=status.HTTP_200_OK)
def update_existing_pipeline(
    pipeline_id: int,
    pipeline_data: PipelineCreate,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing pipeline
    
    Args:
        pipeline_id: The ID of the pipeline to update
        pipeline_data: Updated pipeline configuration
        
    Returns:
        Updated pipeline details
    """
    return update_pipeline(pipeline_id, pipeline_data, current_user.id, db)


@router.delete("/{pipeline_id}", status_code=status.HTTP_200_OK)
def delete_existing_pipeline(
    pipeline_id: int,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Delete a pipeline
    
    Args:
        pipeline_id: The ID of the pipeline to delete
        
    Returns:
        Success message
    """
    return delete_pipeline(pipeline_id, current_user.id, db)
