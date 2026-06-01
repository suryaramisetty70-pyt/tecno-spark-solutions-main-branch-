"""
Agent Marketplace Service
Manages agent discovery, ratings, installation, and monetization
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AgentMarketplaceService:
    """Service for agent marketplace operations"""

    def __init__(self):
        self.agents_db = {}  # In-memory for MVP, will use database later
        self.ratings_db = {}
        self.installs_db = {}

    def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register agent in marketplace"""
        try:
            agent_id = agent_data.get("agent_id")
            agent_name = agent_data.get("name")

            agent = {
                "id": agent_id,
                "name": agent_name,
                "category": agent_data.get("category"),
                "description": agent_data.get("description"),
                "capabilities": agent_data.get("capabilities", []),
                "tools": agent_data.get("tools", []),
                "version": agent_data.get("version", "1.0.0"),
                "author": agent_data.get("author", "Tecno Spark"),
                "rating": 0.0,
                "installs": 0,
                "downloads": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "verified": True,
                "featured": False,
                "price": agent_data.get("price", 0),  # 0 = free, >0 = paid
                "status": "active"
            }

            self.agents_db[agent_id] = agent
            logger.info(f"Registered agent: {agent_name}")
            return {"status": "success", "agent": agent}
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return {"status": "error", "message": str(e)}

    def search_agents(self, query: str = "", category: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """Search agents in marketplace"""
        try:
            results = []
            for agent in self.agents_db.values():
                # Filter by category
                if category and agent.get("category") != category:
                    continue

                # Filter by query
                if query:
                    if query.lower() not in agent.get("name", "").lower() and \
                       query.lower() not in agent.get("description", "").lower():
                        continue

                results.append(agent)

            # Sort by rating and installs
            results.sort(key=lambda x: (-x.get("rating", 0), -x.get("installs", 0)))
            return results[:limit]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details"""
        try:
            agent = self.agents_db.get(agent_id)
            if not agent:
                return {"status": "error", "message": "Agent not found"}

            # Get ratings
            agent_ratings = self.ratings_db.get(agent_id, [])
            avg_rating = sum(r["rating"] for r in agent_ratings) / len(agent_ratings) if agent_ratings else 0

            agent["average_rating"] = avg_rating
            agent["review_count"] = len(agent_ratings)
            agent["install_count"] = self.installs_db.get(agent_id, 0)

            return {"status": "success", "agent": agent}
        except Exception as e:
            logger.error(f"Failed to get agent details: {e}")
            return {"status": "error", "message": str(e)}

    def rate_agent(self, agent_id: str, user_id: str, rating: int, review: str = "") -> Dict[str, Any]:
        """Rate an agent"""
        try:
            if not 1 <= rating <= 5:
                return {"status": "error", "message": "Rating must be between 1 and 5"}

            if agent_id not in self.agents_db:
                return {"status": "error", "message": "Agent not found"}

            rating_data = {
                "user_id": user_id,
                "rating": rating,
                "review": review,
                "timestamp": datetime.utcnow().isoformat()
            }

            if agent_id not in self.ratings_db:
                self.ratings_db[agent_id] = []

            self.ratings_db[agent_id].append(rating_data)

            # Update agent rating
            ratings = self.ratings_db[agent_id]
            avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
            self.agents_db[agent_id]["rating"] = avg_rating

            return {"status": "success", "message": "Rating submitted"}
        except Exception as e:
            logger.error(f"Failed to rate agent: {e}")
            return {"status": "error", "message": str(e)}

    def install_agent(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """Install agent for user"""
        try:
            if agent_id not in self.agents_db:
                return {"status": "error", "message": "Agent not found"}

            # Track installation
            if agent_id not in self.installs_db:
                self.installs_db[agent_id] = 0

            self.installs_db[agent_id] += 1
            self.agents_db[agent_id]["installs"] = self.installs_db[agent_id]

            logger.info(f"User {user_id} installed agent {agent_id}")
            return {
                "status": "success",
                "message": "Agent installed successfully",
                "agent_id": agent_id,
                "installed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to install agent: {e}")
            return {"status": "error", "message": str(e)}

    def get_popular_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular agents"""
        try:
            agents = list(self.agents_db.values())
            agents.sort(key=lambda x: (-x.get("rating", 0), -x.get("installs", 0)))
            return agents[:limit]
        except Exception as e:
            logger.error(f"Failed to get popular agents: {e}")
            return []

    def get_agents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get agents by category"""
        try:
            return [a for a in self.agents_db.values() if a.get("category") == category]
        except Exception as e:
            logger.error(f"Failed to get agents by category: {e}")
            return []

    def publish_agent_update(self, agent_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish agent update"""
        try:
            if agent_id not in self.agents_db:
                return {"status": "error", "message": "Agent not found"}

            agent = self.agents_db[agent_id]
            agent.update(update_data)
            agent["updated_at"] = datetime.utcnow().isoformat()

            return {"status": "success", "message": "Agent updated", "agent": agent}
        except Exception as e:
            logger.error(f"Failed to update agent: {e}")
            return {"status": "error", "message": str(e)}


# Marketplace service instance
marketplace_service = AgentMarketplaceService()
