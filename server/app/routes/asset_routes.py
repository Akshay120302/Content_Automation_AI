"""
Pipeline Asset Routes
API endpoints for managing pipeline reference file uploads
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.routes.auth_routes import get_authenticated_user
from app.schemas.asset_schema import (
    AssetUploadRequest,
    AssetUploadUrlResponse,
    AssetConfirmUploadRequest,
    AssetResponse,
    AssetDownloadUrlResponse,
    BulkAssetUploadRequest,
    BulkAssetUploadResponse
)
from app.controllers.asset_controller import (
    generate_upload_url,
    generate_bulk_upload_urls,
    confirm_upload,
    get_pipeline_assets,
    get_download_url,
    delete_asset
)


# Define the router
router = APIRouter(prefix="/pipelines", tags=["Pipeline Assets"])


@router.post(
    "/{pipeline_id}/assets/upload-url",
    response_model=AssetUploadUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate presigned upload URL for a file"
)
def request_upload_url(
    pipeline_id: int,
    file_request: AssetUploadRequest,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Generate a presigned URL for uploading a file directly to S3.
    
    **Workflow:**
    1. Frontend calls this endpoint with file metadata
    2. Backend creates asset record and generates presigned POST URL
    3. Frontend uploads file directly to S3 using the presigned URL
    4. Frontend confirms upload via PATCH endpoint
    
    **Args:**
    - **pipeline_id**: ID of the pipeline
    - **filename**: Original filename
    - **content_type**: MIME type (e.g., image/png)
    - **file_size**: File size in bytes
    
    **Returns:**
    - **asset_id**: Database ID of the asset record
    - **upload_url**: S3 presigned POST URL
    - **upload_fields**: Form fields to include in POST request
    - **s3_key**: S3 object key
    - **expires_in**: URL expiry time in seconds
    """
    return generate_upload_url(pipeline_id, file_request, current_user.id, db)


@router.post(
    "/{pipeline_id}/assets/upload-urls",
    response_model=BulkAssetUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate presigned upload URLs for multiple files"
)
def request_bulk_upload_urls(
    pipeline_id: int,
    bulk_request: BulkAssetUploadRequest,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Generate presigned URLs for uploading multiple files at once.
    
    **Args:**
    - **pipeline_id**: ID of the pipeline
    - **files**: List of file metadata (max 20 files)
    
    **Returns:**
    - **uploads**: List of upload URL responses
    - **total_count**: Number of files
    """
    return generate_bulk_upload_urls(pipeline_id, bulk_request, current_user.id, db)


@router.patch(
    "/{pipeline_id}/assets/{asset_id}/confirm",
    response_model=AssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm file upload to S3"
)
def confirm_asset_upload(
    pipeline_id: int,
    asset_id: int,
    confirm_request: AssetConfirmUploadRequest,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Confirm that file upload to S3 was successful.
    
    Call this endpoint after successfully uploading the file to S3 using the presigned URL.
    This updates the asset status from 'pending' to 'confirmed'.
    
    **Args:**
    - **pipeline_id**: ID of the pipeline
    - **asset_id**: ID of the asset
    - **success**: Whether upload succeeded (default: true)
    - **error_message**: Optional error message if upload failed
    
    **Returns:**
    - Updated asset metadata
    """
    return confirm_upload(pipeline_id, asset_id, confirm_request, current_user.id, db)


@router.get(
    "/{pipeline_id}/assets",
    response_model=List[AssetResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all assets for a pipeline"
)
def list_pipeline_assets(
    pipeline_id: int,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Get all confirmed/uploaded assets for a pipeline.
    
    **Args:**
    - **pipeline_id**: ID of the pipeline
    
    **Returns:**
    - List of asset metadata
    """
    return get_pipeline_assets(pipeline_id, current_user.id, db)


@router.get(
    "/{pipeline_id}/assets/{asset_id}/download-url",
    response_model=AssetDownloadUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate presigned download URL"
)
def request_download_url(
    pipeline_id: int,
    asset_id: int,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Generate a presigned URL for downloading/viewing a file from S3.
    
    **Args:**
    - **pipeline_id**: ID of the pipeline
    - **asset_id**: ID of the asset
    
    **Returns:**
    - **asset_id**: Asset ID
    - **download_url**: S3 presigned GET URL
    - **expires_in**: URL expiry time in seconds (1 hour)
    """
    return get_download_url(pipeline_id, asset_id, current_user.id, db)


@router.delete(
    "/{pipeline_id}/assets/{asset_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an asset"
)
def delete_pipeline_asset(
    pipeline_id: int,
    asset_id: int,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Delete an asset from both database and S3.
    
    **Args:**
    - **pipeline_id**: ID of the pipeline
    - **asset_id**: ID of the asset to delete
    
    **Returns:**
    - Success message
    """
    return delete_asset(pipeline_id, asset_id, current_user.id, db)
