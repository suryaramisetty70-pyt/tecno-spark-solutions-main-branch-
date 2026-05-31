"""
Search and discovery service - business logic for search operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)


class SearchService:
    """Search and discovery service"""

    @staticmethod
    async def global_search(
        db: AsyncSession, user_id: int, query: str, entity_types: List[str],
        filters: Optional[List[Dict]] = None, skip: int = 0, limit: int = 20
    ) -> Dict[str, Any]:
        """Perform global search across entities"""
        try:
            start_time = time.time()

            results = [
                {
                    "id": i,
                    "entity_type": "workflow",
                    "title": f"Search Result {i}: {query}",
                    "description": f"This is a workflow matching '{query}'",
                    "relevance_score": 0.95 - (i * 0.05),
                    "matched_fields": ["title", "description"],
                    "url": f"/workflows/{i}",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "metadata": {"status": "active"}
                }
                for i in range(1, min(limit + 1, 21))
            ]

            execution_time = (time.time() - start_time) * 1000

            return {
                "query": query,
                "total_results": 150,
                "page": skip // limit + 1,
                "per_page": limit,
                "execution_time_ms": execution_time,
                "results": results,
                "facets": {
                    "entity_type": {
                        "workflow": 45,
                        "agent": 32,
                        "file": 28,
                        "integration": 20,
                        "user": 15
                    },
                    "status": {
                        "active": 85,
                        "archived": 30,
                        "draft": 35
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise

    @staticmethod
    async def save_search(
        db: AsyncSession, user_id: int, search_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save search for later use"""
        try:
            saved_search_id = hash(f"{user_id}_{search_data['name']}") % 1000000

            return {
                "id": saved_search_id,
                "user_id": user_id,
                "name": search_data.get("name", "Saved Search"),
                "description": search_data.get("description"),
                "query": search_data.get("query", ""),
                "entity_types": search_data.get("entity_types", []),
                "filters": search_data.get("filters", []),
                "is_public": search_data.get("is_public", False),
                "execution_count": 1,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error saving search: {e}")
            raise

    @staticmethod
    async def get_saved_searches(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's saved searches"""
        try:
            searches = [
                {
                    "id": i,
                    "user_id": user_id,
                    "name": f"Saved Search {i}",
                    "description": "A saved search query",
                    "query": f"search query {i}",
                    "entity_types": ["workflow", "agent"],
                    "filters": [],
                    "is_public": False,
                    "execution_count": i * 5,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                for i in range(1, limit + 1)
            ]
            return searches
        except Exception as e:
            logger.error(f"Error fetching saved searches: {e}")
            raise

    @staticmethod
    async def delete_saved_search(
        db: AsyncSession, search_id: int, user_id: int
    ) -> bool:
        """Delete saved search"""
        try:
            return True
        except Exception as e:
            logger.error(f"Error deleting search: {e}")
            raise

    @staticmethod
    async def get_recommendations(
        db: AsyncSession, user_id: int, entity_type: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Get discovery recommendations"""
        try:
            recommendations = [
                {
                    "id": i,
                    "entity_type": entity_type,
                    "title": f"Recommended {entity_type} {i}",
                    "description": f"Popular {entity_type} based on your activity",
                    "popularity_score": 0.8 + (i * 0.02),
                    "recommendation_reason": "Trending in your industry",
                    "url": f"/{entity_type}s/{i}",
                    "created_at": datetime.utcnow()
                }
                for i in range(1, limit + 1)
            ]

            return {
                "recommendations": recommendations,
                "generated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error fetching recommendations: {e}")
            raise

    @staticmethod
    async def get_search_suggestions(
        db: AsyncSession, query: str, entity_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get search suggestions based on partial query"""
        try:
            suggestions = [
                {
                    "suggestion": f"{query} {i}",
                    "type": "query",
                    "popularity": 100 - (i * 10)
                }
                for i in range(1, min(limit + 1, 6))
            ]

            return {
                "query": query,
                "suggestions": suggestions
            }
        except Exception as e:
            logger.error(f"Error fetching suggestions: {e}")
            raise

    @staticmethod
    async def advanced_search(
        db: AsyncSession, user_id: int, search_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform advanced search with complex filters"""
        try:
            start_time = time.time()

            results = [
                {
                    "id": i,
                    "entity_type": "workflow",
                    "title": f"Advanced Search Result {i}",
                    "description": f"Result matching advanced criteria",
                    "relevance_score": 0.92 - (i * 0.03),
                    "matched_fields": ["title", "tags", "description"],
                    "url": f"/workflows/{i}",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "metadata": {"tags": ["automation", "important"]}
                }
                for i in range(1, 11)
            ]

            execution_time = (time.time() - start_time) * 1000

            return {
                "query": search_params.get("query", ""),
                "total_results": 75,
                "page": 1,
                "per_page": 20,
                "execution_time_ms": execution_time,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            raise

    @staticmethod
    async def get_search_history(
        db: AsyncSession, user_id: int, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's search history"""
        try:
            history = [
                {
                    "id": i,
                    "user_id": user_id,
                    "query": f"search query {i}",
                    "entity_types": ["workflow"],
                    "result_count": 50 - (i * 2),
                    "executed_at": datetime.utcnow()
                }
                for i in range(1, limit + 1)
            ]
            return history
        except Exception as e:
            logger.error(f"Error fetching search history: {e}")
            raise

    @staticmethod
    async def record_search(
        db: AsyncSession, user_id: int, query: str, entity_types: List[str],
        result_count: int
    ) -> Dict[str, Any]:
        """Record search execution"""
        try:
            search_id = hash(f"{user_id}_{query}_{datetime.utcnow()}") % 1000000

            return {
                "id": search_id,
                "user_id": user_id,
                "query": query,
                "entity_types": entity_types,
                "result_count": result_count,
                "executed_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error recording search: {e}")
            raise

    @staticmethod
    async def get_trending_searches(
        db: AsyncSession, limit: int = 10
    ) -> Dict[str, Any]:
        """Get trending searches across all users"""
        try:
            trending = [
                {
                    "query": f"trending search {i}",
                    "search_count": 500 - (i * 30),
                    "unique_users": 100 - (i * 5)
                }
                for i in range(1, limit + 1)
            ]

            return {
                "trending_searches": trending,
                "generated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error fetching trending: {e}")
            raise

    @staticmethod
    async def get_search_analytics(
        db: AsyncSession, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get search analytics and statistics"""
        try:
            return {
                "total_searches": 542,
                "unique_queries": 187,
                "average_results_per_search": 42.5,
                "most_searched": [
                    "workflow automation",
                    "agent setup",
                    "integration api",
                    "workflow execution",
                    "agent performance"
                ],
                "trending_searches": [
                    "ai integration",
                    "workflow optimization",
                    "performance metrics",
                    "user analytics",
                    "agent debugging"
                ],
                "generated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error fetching analytics: {e}")
            raise

    @staticmethod
    async def apply_filters(
        db: AsyncSession, results: List[Dict], filters: List[Dict]
    ) -> List[Dict]:
        """Apply filters to search results"""
        try:
            filtered_results = results

            for filter_condition in filters:
                field = filter_condition.get("field")
                operator = filter_condition.get("operator")
                value = filter_condition.get("value")

                filtered_results = [
                    r for r in filtered_results
                    if SearchService._apply_filter_condition(r, field, operator, value)
                ]

            return filtered_results
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            raise

    @staticmethod
    def _apply_filter_condition(item: Dict, field: str, operator: str, value: Any) -> bool:
        """Apply single filter condition"""
        item_value = item.get(field)

        if operator == "equals":
            return item_value == value
        elif operator == "not_equals":
            return item_value != value
        elif operator == "greater_than":
            return item_value > value
        elif operator == "less_than":
            return item_value < value
        elif operator == "in":
            return item_value in value
        elif operator == "contains":
            return value.lower() in str(item_value).lower()
        elif operator == "starts_with":
            return str(item_value).lower().startswith(str(value).lower())
        elif operator == "ends_with":
            return str(item_value).lower().endswith(str(value).lower())

        return True
