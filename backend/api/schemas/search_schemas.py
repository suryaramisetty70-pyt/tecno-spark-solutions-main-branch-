"""
Search and discovery request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    """Searchable entity types"""
    USER = "user"
    AGENT = "agent"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    FILE = "file"
    NOTIFICATION = "notification"
    DOCUMENT = "document"


class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Filter operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class FilterCondition(BaseModel):
    """Filter condition"""
    field: str = Field(..., min_length=1, max_length=100)
    operator: FilterOperator = Field(...)
    value: Any = Field(...)


class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: Optional[List[EntityType]] = Field(default_factory=list)
    filters: Optional[List[FilterCondition]] = Field(default_factory=list)
    sort_by: Optional[str] = Field(default="relevance")
    sort_order: Optional[SortOrder] = Field(default=SortOrder.DESC)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    include_archived: bool = False


class SearchResultItem(BaseModel):
    """Individual search result"""
    id: int
    entity_type: EntityType
    title: str
    description: Optional[str]
    relevance_score: float
    matched_fields: List[str]
    url: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    total_results: int
    page: int
    per_page: int
    execution_time_ms: float
    results: List[SearchResultItem]
    facets: Optional[Dict[str, Dict[str, int]]] = None


class SavedSearchRequest(BaseModel):
    """Save search request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: List[EntityType] = Field(default_factory=list)
    filters: Optional[List[FilterCondition]] = Field(default_factory=list)
    is_public: bool = False


class SavedSearchResponse(BaseModel):
    """Saved search response"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    query: str
    entity_types: List[str]
    filters: Optional[List[Dict[str, Any]]]
    is_public: bool
    execution_count: int
    created_at: datetime
    updated_at: datetime


class DiscoveryRequest(BaseModel):
    """Discovery/recommendations request"""
    entity_type: EntityType
    based_on: Optional[List[int]] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=50)
    include_trending: bool = True


class DiscoveryItem(BaseModel):
    """Discovery item"""
    id: int
    entity_type: EntityType
    title: str
    description: Optional[str]
    popularity_score: float
    recommendation_reason: str
    url: str
    created_at: datetime


class DiscoveryResponse(BaseModel):
    """Discovery response"""
    recommendations: List[DiscoveryItem]
    generated_at: datetime


class SearchSuggestionRequest(BaseModel):
    """Search suggestion request"""
    query: str = Field(..., min_length=1, max_length=200)
    entity_types: Optional[List[EntityType]] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=50)


class SearchSuggestion(BaseModel):
    """Search suggestion"""
    suggestion: str
    type: str
    popularity: int


class SearchSuggestionResponse(BaseModel):
    """Search suggestion response"""
    query: str
    suggestions: List[SearchSuggestion]


class AdvancedSearchRequest(BaseModel):
    """Advanced search request"""
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: List[EntityType] = Field(...)
    filters: List[FilterCondition] = Field(default_factory=list)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: str = Field(default="relevance")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class SearchHistoryResponse(BaseModel):
    """Search history"""
    id: int
    user_id: int
    query: str
    entity_types: List[str]
    result_count: int
    executed_at: datetime


class SearchAnalyticsResponse(BaseModel):
    """Search analytics"""
    total_searches: int
    unique_queries: int
    average_results_per_search: float
    most_searched: List[str]
    trending_searches: List[str]
    generated_at: datetime
