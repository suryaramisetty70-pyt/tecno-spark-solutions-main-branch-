"""
Agent Marketplace API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from services.marketplace_service import marketplace_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


@router.get("/agents")
async def search_agents(
    query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(20, le=100)
):
    """Search agents in marketplace"""
    agents = marketplace_service.search_agents(query=query or "", category=category or "", limit=limit)
    return {"status": "success", "agents": agents, "count": len(agents)}


@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get agent details"""
    result = marketplace_service.get_agent_details(agent_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.get("/agents/category/{category}")
async def get_agents_by_category(category: str):
    """Get agents by category"""
    agents = marketplace_service.get_agents_by_category(category)
    return {"status": "success", "category": category, "agents": agents, "count": len(agents)}


@router.get("/popular")
async def get_popular_agents(limit: int = Query(10, le=50)):
    """Get popular agents"""
    agents = marketplace_service.get_popular_agents(limit)
    return {"status": "success", "agents": agents, "count": len(agents)}


@router.post("/agents/{agent_id}/install")
async def install_agent(agent_id: str, user_id: str = Query(...)):
    """Install agent"""
    result = marketplace_service.install_agent(agent_id, user_id)
    return result


@router.post("/agents/{agent_id}/rate")
async def rate_agent(agent_id: str, rating: int = Query(..., ge=1, le=5), user_id: str = Query(...), review: Optional[str] = Query(None)):
    """Rate an agent"""
    result = marketplace_service.rate_agent(agent_id, user_id, rating, review or "")
    return result


@router.get("/categories")
async def get_categories():
    """Get all agent categories"""
    categories = set()
    for agent in list(marketplace_service.agents_db.values()):
        categories.add(agent.get("category"))
    return {"status": "success", "categories": sorted(list(categories))}


@router.get("/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    agents = list(marketplace_service.agents_db.values())
    total_installs = sum(a.get("installs", 0) for a in agents)
    avg_rating = sum(a.get("rating", 0) for a in agents) / len(agents) if agents else 0

    return {
        "status": "success",
        "total_agents": len(agents),
        "total_installs": total_installs,
        "average_rating": avg_rating,
        "categories": len(set(a.get("category") for a in agents))
    }
