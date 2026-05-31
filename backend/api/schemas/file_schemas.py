"""
File management request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    """File type enum"""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    OTHER = "other"


class FileStatus(str, Enum):
    """File status enum"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"


class StorageType(str, Enum):
    """Storage type enum"""
    LOCAL = "local"
    S3 = "s3"
    CLOUD = "cloud"


class FileUploadRequest(BaseModel):
    """File upload request"""
    filename: str = Field(..., min_length=1, max_length=500)
    file_type: FileType = Field(...)
    description: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = Field(default_factory=list)
    is_public: bool = False


class FileResponse(BaseModel):
    """File response"""
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_type: FileType
    file_size: int
    mime_type: str
    status: FileStatus
    description: Optional[str]
    tags: Optional[List[str]]
    is_public: bool
    url: str
    storage_path: str
    storage_type: StorageType
    uploaded_at: datetime
    updated_at: datetime


class FileListResponse(BaseModel):
    """File list response"""
    total: int
    page: int
    per_page: int
    files: List[FileResponse]


class FileShareRequest(BaseModel):
    """Share file request"""
    file_id: int = Field(...)
    share_with_user_id: int = Field(...)
    permission: str = Field(default="view")


class FileShareResponse(BaseModel):
    """File share response"""
    id: int
    file_id: int
    file_owner_id: int
    shared_with_user_id: int
    permission: str
    shared_at: datetime


class FileVersionRequest(BaseModel):
    """File version request"""
    file_id: int = Field(...)
    description: Optional[str] = None


class FileVersionResponse(BaseModel):
    """File version response"""
    id: int
    file_id: int
    version_number: int
    size: int
    created_at: datetime
    created_by_user_id: int


class FilePermissionRequest(BaseModel):
    """File permission request"""
    file_id: int = Field(...)
    user_id: Optional[int] = None
    permission: str = Field(...)


class FileSearchRequest(BaseModel):
    """File search request"""
    query: str = Field(..., min_length=1, max_length=255)
    file_type: Optional[FileType] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class FileMetadataResponse(BaseModel):
    """File metadata response"""
    file_id: int
    filename: str
    size: int
    mime_type: str
    created_at: datetime
    modified_at: datetime
    storage_location: str
    checksum: str
