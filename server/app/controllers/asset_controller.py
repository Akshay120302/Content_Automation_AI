"""
Pipeline Asset Controller
Business logic for managing pipeline reference file uploads to S3
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.pipeline import Pipeline, PipelineAsset, AssetUploadStatus, AssetRole
from app.schemas.asset_schema import (
    AssetUploadRequest,
    AssetUploadUrlResponse,
    AssetConfirmUploadRequest,
    AssetResponse,
    AssetDownloadUrlResponse,
    BulkAssetUploadRequest,
    BulkAssetUploadResponse
)
from app.utils.s3_storage import get_s3_client, determine_asset_role, validate_file_upload
from app.config import settings


def verify_pipeline_ownership(pipeline_id: int, user_id: UUID, db: Session) -> Pipeline:
    """
    Verify that the pipeline exists and belongs to the user
    
    Args:
        pipeline_id: Pipeline ID
        user_id: User UUID
        db: Database session
    
    Returns:
        Pipeline object if found and authorized
    
    Raises:
        HTTPException: If pipeline not found or unauthorized
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
    
    return pipeline


def generate_upload_url(
    pipeline_id: int,
    file_request: AssetUploadRequest,
    user_id: UUID,
    db: Session
) -> AssetUploadUrlResponse:
    """
    Generate presigned upload URL for a single file
    
    Args:
        pipeline_id: Pipeline ID
        file_request: File upload request data
        user_id: User UUID
        db: Database session
    
    Returns:
        Upload URL response with presigned POST data
    """
    # Verify pipeline ownership
    pipeline = verify_pipeline_ownership(pipeline_id, user_id, db)
    
    # Validate file parameters
    is_valid, error_msg = validate_file_upload(
        file_request.filename,
        file_request.content_type,
        file_request.file_size
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Get S3 client
    s3 = get_s3_client()
    if not s3.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File storage service is not available. Please configure AWS S3."
        )
    
    # Determine asset role FIRST (needed for S3 key generation)
    role = determine_asset_role(file_request.content_type, file_request.filename)
    
    # Generate S3 key with role in path
    s3_key = s3.generate_s3_key(str(user_id), pipeline_id, file_request.filename, role)
    
    # Generate presigned POST URL
    presigned_post = s3.generate_presigned_post(
        s3_key=s3_key,
        content_type=file_request.content_type,
        file_size=file_request.file_size
    )
    
    if not presigned_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )
    
    # Create asset record in database with pending status
    asset = PipelineAsset(
        pipeline_id=pipeline_id,
        user_id=user_id,
        filename=file_request.filename,
        content_type=file_request.content_type,
        file_size=file_request.file_size,
        s3_key=s3_key,
        s3_bucket=settings.S3_BUCKET,
        upload_status=AssetUploadStatus.pending,
        role=AssetRole[role]
    )
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    # Return upload URL with asset ID
    return AssetUploadUrlResponse(
        asset_id=asset.id,
        upload_url=presigned_post['url'],
        upload_fields=presigned_post['fields'],
        s3_key=s3_key,
        expires_in=settings.S3_PRESIGNED_URL_EXPIRY
    )


def generate_bulk_upload_urls(
    pipeline_id: int,
    bulk_request: BulkAssetUploadRequest,
    user_id: UUID,
    db: Session
) -> BulkAssetUploadResponse:
    """
    Generate presigned upload URLs for multiple files
    
    Args:
        pipeline_id: Pipeline ID
        bulk_request: Bulk upload request with list of files
        user_id: User UUID
        db: Database session
    
    Returns:
        Bulk upload response with URLs for all files
    """
    upload_responses = []
    
    for file_request in bulk_request.files:
        try:
            upload_response = generate_upload_url(pipeline_id, file_request, user_id, db)
            upload_responses.append(upload_response)
        except HTTPException as e:
            # If one file fails, rollback and raise error
            db.rollback()
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Failed to process '{file_request.filename}': {e.detail}"
            )
    
    return BulkAssetUploadResponse(
        uploads=upload_responses,
        total_count=len(upload_responses)
    )


def confirm_upload(
    pipeline_id: int,
    asset_id: int,
    confirm_request: AssetConfirmUploadRequest,
    user_id: UUID,
    db: Session
) -> AssetResponse:
    """
    Confirm that file upload to S3 was successful
    
    Args:
        pipeline_id: Pipeline ID
        asset_id: Asset ID
        confirm_request: Confirmation request
        user_id: User UUID
        db: Database session
    
    Returns:
        Updated asset response
    """
    # Verify pipeline ownership
    verify_pipeline_ownership(pipeline_id, user_id, db)
    
    # Find the asset
    asset = db.query(PipelineAsset).filter(
        PipelineAsset.id == asset_id,
        PipelineAsset.pipeline_id == pipeline_id,
        PipelineAsset.user_id == user_id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Update status
    if confirm_request.success:
        asset.upload_status = AssetUploadStatus.confirmed
        asset.uploaded_at = datetime.utcnow()
    else:
        asset.upload_status = AssetUploadStatus.failed
    
    db.commit()
    db.refresh(asset)
    
    return AssetResponse.from_orm(asset)


def get_pipeline_assets(
    pipeline_id: int,
    user_id: UUID,
    db: Session
) -> List[AssetResponse]:
    """
    Get all assets for a pipeline
    
    Args:
        pipeline_id: Pipeline ID
        user_id: User UUID
        db: Database session
    
    Returns:
        List of asset responses
    """
    # Verify pipeline ownership
    verify_pipeline_ownership(pipeline_id, user_id, db)
    
    # Get all assets
    assets = db.query(PipelineAsset).filter(
        PipelineAsset.pipeline_id == pipeline_id,
        PipelineAsset.upload_status == AssetUploadStatus.confirmed
    ).order_by(PipelineAsset.created_at.desc()).all()
    
    return [AssetResponse.from_orm(asset) for asset in assets]


def get_download_url(
    pipeline_id: int,
    asset_id: int,
    user_id: UUID,
    db: Session
) -> AssetDownloadUrlResponse:
    """
    Generate presigned download URL for an asset
    
    Args:
        pipeline_id: Pipeline ID
        asset_id: Asset ID
        user_id: User UUID
        db: Database session
    
    Returns:
        Download URL response
    """
    # Verify pipeline ownership
    verify_pipeline_ownership(pipeline_id, user_id, db)
    
    # Find the asset
    asset = db.query(PipelineAsset).filter(
        PipelineAsset.id == asset_id,
        PipelineAsset.pipeline_id == pipeline_id,
        PipelineAsset.user_id == user_id,
        PipelineAsset.upload_status == AssetUploadStatus.confirmed
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found or not yet uploaded"
        )
    
    # Get S3 client
    s3 = get_s3_client()
    if not s3.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File storage service is not available"
        )
    
    # Generate presigned GET URL
    download_url = s3.generate_presigned_url(asset.s3_key, expiry=3600)
    
    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )
    
    return AssetDownloadUrlResponse(
        asset_id=asset.id,
        download_url=download_url,
        expires_in=3600
    )


def delete_asset(
    pipeline_id: int,
    asset_id: int,
    user_id: UUID,
    db: Session
) -> dict:
    """
    Delete an asset from database and S3
    
    Args:
        pipeline_id: Pipeline ID
        asset_id: Asset ID
        user_id: User UUID
        db: Database session
    
    Returns:
        Success message
    """
    # Verify pipeline ownership
    verify_pipeline_ownership(pipeline_id, user_id, db)
    
    # Find the asset
    asset = db.query(PipelineAsset).filter(
        PipelineAsset.id == asset_id,
        PipelineAsset.pipeline_id == pipeline_id,
        PipelineAsset.user_id == user_id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Delete from S3 if it was uploaded
    if asset.upload_status in [AssetUploadStatus.confirmed, AssetUploadStatus.uploaded]:
        s3 = get_s3_client()
        if s3.is_available():
            s3.delete_file(asset.s3_key)
    
    # Delete from database
    db.delete(asset)
    db.commit()
    
    return {"message": "Asset deleted successfully"}
