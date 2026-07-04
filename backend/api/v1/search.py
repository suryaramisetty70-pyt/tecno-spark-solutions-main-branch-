"""
Search and discovery API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.database import get_db_session
from api.schemas.search_schemas import (
    SearchRequest, SearchResponse, SavedSearchRequest, SavedSearchResponse,
    DiscoveryRequest, DiscoveryResponse, SearchSuggestionRequest,
    SearchSuggestionResponse, AdvancedSearchRequest, SearchHistoryResponse,
    SearchAnalyticsResponse
)
from services.search_service import SearchService
from api.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.post("/global", response_model=SearchResponse)
async def global_search(
    search_request: SearchRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Perform global search across all entities"""
    try:
        result = await SearchService.global_search(
            db, current_user.id, search_request.query,
            [e.value for e in search_request.entity_types],
            [f.dict() for f in search_request.filters] if search_request.filters else None,
            search_request.skip, search_request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advanced", response_model=SearchResponse)
async def advanced_search(
    search_request: AdvancedSearchRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Perform advanced search with complex filters"""
    try:
        result = await SearchService.advanced_search(
            db, current_user.id, search_request.dict()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/saved", response_model=SavedSearchResponse, status_code=201)
async def save_search(
    save_request: SavedSearchRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Save search for later"""
    try:
        result = await SearchService.save_search(db, current_user.id, save_request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/saved", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's saved searches"""
    try:
        searches = await SearchService.get_saved_searches(db, current_user.id, skip, limit)
        return searches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/saved/{search_id}", status_code=204)
async def delete_saved_search(
    search_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete saved search"""
    try:
        success = await SearchService.delete_saved_search(db, search_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Search not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggestions", response_model=SearchSuggestionResponse)
async def get_suggestions(
    suggestion_request: SearchSuggestionRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get search suggestions"""
    try:
        result = await SearchService.get_search_suggestions(
            db, suggestion_request.query,
            [e.value for e in suggestion_request.entity_types],
            suggestion_request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover", response_model=DiscoveryResponse)
async def get_discoveries(
    discovery_request: DiscoveryRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get discovery recommendations"""
    try:
        result = await SearchService.get_recommendations(
            db, current_user.id, discovery_request.entity_type.value,
            discovery_request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get search history"""
    try:
        history = await SearchService.get_search_history(db, current_user.id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_searches(
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get trending searches"""
    try:
        result = await SearchService.get_trending_searches(db, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=SearchAnalyticsResponse)
async def get_search_analytics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get search analytics"""
    try:
        analytics = await SearchService.get_search_analytics(db, current_user.id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular")
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get most popular searches"""
    try:
        analytics = await SearchService.get_search_analytics(db)
        return {
            "popular_searches": analytics.get("most_searched", []),
            "trending_searches": analytics.get("trending_searches", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
