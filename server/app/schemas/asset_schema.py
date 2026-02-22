"""
Pipeline Asset Schemas
Request/Response models for file upload operations
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID


class AssetUploadRequest(BaseModel):
    """Request to generate upload URL for a file"""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    content_type: str = Field(..., description="MIME type (e.g., image/png)")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Ensure filename doesn't contain path separators"""
        if '/' in v or '\\' in v:
            raise ValueError("Filename cannot contain path separators")
        return v


class AssetUploadUrlResponse(BaseModel):
    """Response containing presigned upload URL"""
    asset_id: int = Field(..., description="Database ID of the asset record")
    upload_url: str = Field(..., description="S3 presigned POST URL")
    upload_fields: Dict[str, str] = Field(..., description="Fields to include in POST request")
    s3_key: str = Field(..., description="S3 object key for this file")
    expires_in: int = Field(..., description="URL expiry time in seconds")


class AssetConfirmUploadRequest(BaseModel):
    """Request to confirm successful upload"""
    success: bool = Field(default=True, description="Whether upload succeeded")
    error_message: Optional[str] = Field(None, description="Error message if upload failed")


class AssetResponse(BaseModel):
    """Response model for asset metadata"""
    id: int
    pipeline_id: int
    user_id: UUID
    filename: str
    content_type: str
    file_size: int
    role: str
    upload_status: str
    created_at: datetime
    uploaded_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AssetDownloadUrlResponse(BaseModel):
    """Response containing presigned download URL"""
    asset_id: int
    download_url: str
    expires_in: int = Field(..., description="URL expiry time in seconds")


class BulkAssetUploadRequest(BaseModel):
    """Request to generate upload URLs for multiple files"""
    files: List[AssetUploadRequest] = Field(..., min_length=1, max_length=20, description="List of files to upload")


class BulkAssetUploadResponse(BaseModel):
    """Response with upload URLs for multiple files"""
    uploads: List[AssetUploadUrlResponse]
    total_count: int
