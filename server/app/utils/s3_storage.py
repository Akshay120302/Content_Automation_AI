"""
AWS S3 Utility Module
Handles file storage operations using presigned URLs for direct browser-to-S3 uploads
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import uuid
from typing import Dict, Optional, Tuple
import mimetypes
import os
from io import BytesIO

from app.config import settings


class S3Client:
    """AWS S3 client for managing file uploads and downloads"""
    
    def __init__(self):
        """Initialize S3 client with credentials from settings"""
        self.s3_client = None
        self.bucket = settings.S3_BUCKET
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize boto3 S3 client"""
        try:
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                print("⚠️  AWS credentials not configured. S3 features will be disabled.")
                return
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket)
            print(f"✅ S3 client initialized successfully (Bucket: {self.bucket})")
            
        except NoCredentialsError:
            print("❌ AWS credentials not found")
            self.s3_client = None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ S3 bucket '{self.bucket}' not found")
            elif error_code == '403':
                print(f"❌ Access denied to S3 bucket '{self.bucket}'")
            else:
                print(f"❌ S3 error: {e}")
            self.s3_client = None
        except Exception as e:
            print(f"❌ Failed to initialize S3 client: {e}")
            self.s3_client = None
    
    def is_available(self) -> bool:
        """Check if S3 client is available and configured"""
        return self.s3_client is not None
    
    def generate_s3_key(self, user_id: str, pipeline_id: int, filename: str, role: str = "other") -> str:
        """
        Generate a unique S3 key for the file
        Format: users/{user_id}/pipelines/{pipeline_id}/{role}/{uuid}_{filename}
        
        Args:
            user_id: User UUID
            pipeline_id: Pipeline ID
            filename: Original filename
            role: Asset role (e.g., reference_image, reference_video)
        """
        # Sanitize filename
        safe_filename = os.path.basename(filename)
        unique_id = uuid.uuid4()
        
        return f"users/{user_id}/pipelines/{pipeline_id}/{role}/{unique_id}_{safe_filename}"

    def generate_run_s3_key(
        self,
        user_id: str,
        pipeline_id: int,
        run_id: str,
        filename: str,
        role: str
    ) -> str:
        """
        Generate a unique S3 key for a specific run.
        Format: users/{user_id}/pipelines/{pipeline_id}/runs/{run_id}/{role}/{uuid}_{filename}
        """
        safe_filename = os.path.basename(filename)
        unique_id = uuid.uuid4()
        return f"users/{user_id}/pipelines/{pipeline_id}/runs/{run_id}/{role}/{unique_id}_{safe_filename}"

    def upload_file(self, file_path: str, s3_key: str, content_type: Optional[str] = None) -> Optional[str]:
        """
        Upload a local file to S3 and return a presigned URL.
        """
        if not self.is_available():
            return None

        content_type = content_type or mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        try:
            self.s3_client.upload_file(
                Filename=file_path,
                Bucket=self.bucket,
                Key=s3_key,
                ExtraArgs={"ContentType": content_type}
            )
            return self.generate_presigned_url(s3_key)
        except ClientError as e:
            print(f"❌ Error uploading file to S3: {e}")
            return None

    def upload_bytes(self, data: bytes, s3_key: str, content_type: str) -> Optional[str]:
        """
        Upload bytes to S3 and return a presigned URL.
        """
        if not self.is_available():
            return None

        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=data,
                ContentType=content_type
            )
            return self.generate_presigned_url(s3_key)
        except ClientError as e:
            print(f"❌ Error uploading bytes to S3: {e}")
            return None
    
    def generate_presigned_post(
        self,
        s3_key: str,
        content_type: str,
        file_size: int,
        expiry: int = None
    ) -> Optional[Dict]:
        """
        Generate a presigned POST URL for direct browser upload to S3
        
        Args:
            s3_key: The S3 object key (path)
            content_type: MIME type of the file
            file_size: Size of file in bytes
            expiry: URL expiration time in seconds (default: from settings)
        
        Returns:
            Dictionary with 'url' and 'fields' for the POST request
            None if S3 is not available
        """
        if not self.is_available():
            return None
        
        expiry = expiry or settings.S3_PRESIGNED_URL_EXPIRY
        max_size = settings.S3_MAX_FILE_SIZE
        
        try:
            # Generate presigned POST
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=self.bucket,
                Key=s3_key,
                Fields={
                    "Content-Type": content_type
                },
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 1, max_size]  # 1 byte to max_size
                ],
                ExpiresIn=expiry
            )
            
            # Fix URL to include region (boto3 sometimes omits it)
            # Change s3.amazonaws.com to s3.{region}.amazonaws.com
            if 's3.amazonaws.com' in presigned_post['url'] and settings.AWS_REGION:
                presigned_post['url'] = presigned_post['url'].replace(
                    's3.amazonaws.com',
                    f's3.{settings.AWS_REGION}.amazonaws.com'
                )
            
            return presigned_post
        
        except ClientError as e:
            print(f"❌ Error generating presigned POST: {e}")
            return None
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiry: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned GET URL for downloading/viewing a file
        
        Args:
            s3_key: The S3 object key (path)
            expiry: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL string or None if error
        """
        if not self.is_available():
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key
                },
                ExpiresIn=expiry
            )
            return url
        
        except ClientError as e:
            print(f"❌ Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: The S3 object key (path)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            print(f"❌ Error deleting file from S3: {e}")
            return False
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Check if a file exists in S3
        
        Args:
            s3_key: The S3 object key (path)
        
        Returns:
            True if file exists, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError:
            return False
    
    def get_file_metadata(self, s3_key: str) -> Optional[Dict]:
        """
        Get metadata about a file in S3
        
        Args:
            s3_key: The S3 object key (path)
        
        Returns:
            Dictionary with file metadata or None
        """
        if not self.is_available():
            return None
        
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag')
            }
        except ClientError as e:
            print(f"❌ Error getting file metadata: {e}")
            return None


# Global S3 client instance
s3_client = S3Client()


def get_s3_client() -> S3Client:
    """Dependency to get S3 client"""
    return s3_client


def determine_asset_role(content_type: str, filename: str) -> str:
    """
    Determine the asset role based on content type and filename
    
    Args:
        content_type: MIME type of the file
        filename: Name of the file
    
    Returns:
        Asset role string
    """
    if content_type.startswith('image/'):
        return 'reference_image'
    elif content_type.startswith('video/'):
        return 'reference_video'
    elif content_type.startswith('audio/'):
        return 'reference_audio'
    elif content_type in ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain', 'text/markdown']:
        return 'reference_document'
    else:
        return 'reference_other'


def validate_file_upload(filename: str, content_type: str, file_size: int) -> tuple[bool, Optional[str]]:
    """
    Validate file upload parameters
    
    Args:
        filename: Name of the file
        content_type: MIME type
        file_size: Size in bytes
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    if file_size > settings.S3_MAX_FILE_SIZE:
        max_mb = settings.S3_MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File size exceeds maximum limit of {max_mb}MB"
    
    if file_size <= 0:
        return False, "Invalid file size"
    
    # Check filename
    if not filename or len(filename) > 255:
        return False, "Invalid filename"
    
    # Check content type
    allowed_types = [
        'image/', 'video/', 'audio/',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument',
        'text/plain',
        'text/markdown'
    ]
    
    if not any(content_type.startswith(t) for t in allowed_types):
        return False, f"File type '{content_type}' is not allowed"
    
    return True, None
