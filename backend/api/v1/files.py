"""
File management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from api.schemas.file_schemas import (
    FileUploadRequest, FileResponse, FileListResponse, FileShareRequest,
    FileSearchRequest, FileMetadataResponse
)
from services.file_service import FileService
from api.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/api/v1/files", tags=["files"])


@router.post("/upload", response_model=FileResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    description: str = Query(None),
    is_public: bool = Query(False),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload file"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        result = await FileService.upload_file(
            db, current_user.id, file.filename, "document",
            file.size or 0, file.content_type or "application/octet-stream",
            description, [], is_public
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=FileListResponse)
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user files"""
    try:
        result = await FileService.list_user_files(db, current_user.id, skip, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file details"""
    try:
        file_data = await FileService.get_file(db, file_id, current_user.id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        return file_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete file"""
    try:
        success = await FileService.delete_file(db, file_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{file_id}/share")
async def share_file(
    file_id: int,
    share_request: FileShareRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Share file with another user"""
    try:
        result = await FileService.share_file(
            db, file_id, current_user.id, share_request.share_with_user_id,
            share_request.permission
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shared/with-me")
async def get_shared_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get files shared with user"""
    try:
        files = await FileService.get_shared_files(db, current_user.id, skip, limit)
        return {
            "total": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=list)
async def search_files(
    search_request: FileSearchRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search files"""
    try:
        results = await FileService.search_files(
            db, current_user.id, search_request.query,
            search_request.skip, search_request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/metadata", response_model=FileMetadataResponse)
async def get_file_metadata(
    file_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file metadata"""
    try:
        metadata = await FileService.get_file_metadata(db, file_id, current_user.id)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{file_id}/tags")
async def update_file_tags(
    file_id: int,
    tags: list = Query(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update file tags"""
    try:
        result = await FileService.update_file_tags(db, file_id, current_user.id, tags)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{file_id}/versions")
async def create_version(
    file_id: int,
    description: str = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new file version"""
    try:
        version = await FileService.create_file_version(db, file_id, current_user.id, description)
        return version
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/versions", response_model=list)
async def get_versions(
    file_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file versions"""
    try:
        versions = await FileService.get_file_versions(db, file_id)
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
