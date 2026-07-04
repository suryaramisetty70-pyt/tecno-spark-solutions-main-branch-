"""
PHASE 1: Agent Scalability Service
Dynamic agent registry, caching, and ML-based routing
"""

import json
from typing import List, Dict, Optional
import asyncio
import numpy as np
from sentence_transformers import SentenceTransformer

class AgentRegistryService:
    """
    Dynamic registry for 1000+ agents
    Replaces hardcoded agent_factory.py lists
    """

    def __init__(self, redis_client, db_session, cache_ttl=3600):
        self.redis = redis_client
        self.db = db_session
        self.cache_ttl = cache_ttl

        # Load embedding model once (free, 22MB)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    async def load_all_agents(self) -> Dict:
        """Load all 1000 agents from DB into memory (once on startup)"""
        agents = {}

        # Query all agents from database
        agent_rows = self.db.query(AgentV2).filter(
            AgentV2.status == "active"
        ).all()

        for agent in agent_rows:
            agents[agent.agent_id] = {
                "id": agent.id,
                "name": agent.name,
                "category": agent.category_id,
                "capabilities": agent.capabilities,
                "tools": agent.tools,
                "version": agent.version,
                "organization_id": agent.organization_id
            }

        return agents

    async def get_agent(self, agent_id: str, org_id: int = None) -> Optional[Dict]:
        """Get agent from cache → DB"""

        # Try Redis cache first
        cache_key = f"agent:{agent_id}:org:{org_id}"
        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        # Query database
        query = self.db.query(AgentV2).filter(AgentV2.agent_id == agent_id)

        if org_id:
            query = query.filter(
                (AgentV2.organization_id == org_id) |
                (AgentV2.is_public == True)
            )

        agent = query.first()

        if agent:
            agent_dict = {
                "id": agent.id,
                "agent_id": agent.agent_id,
                "name": agent.name,
                "capabilities": agent.capabilities,
                "tools": agent.tools
            }

            # Cache for 1 hour
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(agent_dict)
            )

            return agent_dict

        return None

    async def search_agents(self, query: str, org_id: int = None, limit: int = 10) -> List[Dict]:
        """Full-text search agents by name/description"""

        search_query = self.db.query(AgentV2).filter(
            (AgentV2.name.ilike(f"%{query}%")) |
            (AgentV2.description.ilike(f"%{query}%"))
        )

        if org_id:
            search_query = search_query.filter(
                (AgentV2.organization_id == org_id) |
                (AgentV2.is_public == True)
            )

        agents = search_query.limit(limit).all()

        return [
            {
                "id": a.id,
                "agent_id": a.agent_id,
                "name": a.name,
                "rating": a.rating,
                "download_count": a.download_count
            }
            for a in agents
        ]

    async def get_agents_by_category(self, category_id: int, org_id: int = None) -> List[Dict]:
        """Get all agents in a category"""

        query = self.db.query(AgentV2).filter(
            AgentV2.category_id == category_id,
            AgentV2.status == "active"
        )

        if org_id:
            query = query.filter(
                (AgentV2.organization_id == org_id) |
                (AgentV2.is_public == True)
            )

        agents = query.all()

        return [
            {
                "id": a.id,
                "agent_id": a.agent_id,
                "name": a.name,
                "rating": a.rating
            }
            for a in agents
        ]

    async def get_popular_agents(self, limit: int = 10, org_id: int = None) -> List[Dict]:
        """Get trending agents by rating/downloads"""

        query = self.db.query(AgentV2).filter(
            AgentV2.status == "active"
        ).order_by(
            AgentV2.rating.desc(),
            AgentV2.download_count.desc()
        )

        if org_id:
            query = query.filter(
                (AgentV2.organization_id == org_id) |
                (AgentV2.is_public == True)
            )

        agents = query.limit(limit).all()

        return [
            {
                "id": a.id,
                "agent_id": a.agent_id,
                "name": a.name,
                "rating": a.rating,
                "download_count": a.download_count
            }
            for a in agents
        ]

    async def register_agent(self, user_id: int, agent_id: int, org_id: int) -> bool:
        """Register/enable agent for user"""

        registration = AgentRegistrationV2(
            organization_id=org_id,
            user_id=user_id,
            agent_id=agent_id,
            enabled=True
        )

        self.db.add(registration)
        self.db.commit()

        # Clear cache
        self.redis.delete(f"user_agents:{user_id}:org:{org_id}")

        return True

    async def get_user_agents(self, user_id: int, org_id: int) -> List[Dict]:
        """Get all registered agents for user"""

        # Try cache first
        cache_key = f"user_agents:{user_id}:org:{org_id}"
        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        # Query from DB
        registrations = self.db.query(AgentRegistrationV2).filter(
            AgentRegistrationV2.user_id == user_id,
            AgentRegistrationV2.organization_id == org_id,
            AgentRegistrationV2.enabled == True
        ).all()

        agents = []
        for reg in registrations:
            agent = self.db.query(AgentV2).get(reg.agent_id)
            if agent:
                agents.append({
                    "id": agent.id,
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "is_favorite": reg.is_favorite,
                    "priority": reg.priority
                })

        # Cache
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(agents)
        )

        return agents


class IntentClassifier:
    """
    ML-based intent classification using free sentence-transformers
    Replaces O(n) keyword matching
    """

    def __init__(self, chromadb_client):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.chromadb = chromadb_client

    async def classify_intent(self, user_intent: str, org_agents: List[Dict]) -> List[tuple]:
        """
        Embed intent and find similar agents
        Returns: [(agent_id, similarity_score), ...]
        """

        # Embed the user intent (free, ~50ms locally)
        intent_embedding = self.encoder.encode(user_intent)

        # Get agent description embeddings from ChromaDB
        agent_texts = [f"{a['name']} {' '.join(a.get('capabilities', []))}" for a in org_agents]

        # Query ChromaDB for most similar agents
        results = self.chromadb.query(
            query_embeddings=[intent_embedding.tolist()],
            n_results=min(5, len(org_agents))
        )

        scored_agents = []
        for i, agent_id in enumerate(results['ids'][0]):
            similarity = results['distances'][0][i]
            scored_agents.append((agent_id, 1 - similarity))  # Convert distance to similarity

        return sorted(scored_agents, key=lambda x: x[1], reverse=True)


class MultiAgentCoordinator:
    """
    Execute multiple agents in parallel (not sequential)
    Uses asyncio.gather for true parallelism
    """

    def __init__(self, timeout_seconds: int = 30):
        self.timeout = timeout_seconds

    async def execute_parallel(self, agents: List, user_input: str, shared_context: Dict) -> Dict:
        """
        Execute agents in parallel with timeout/retry
        """

        tasks = []

        for agent in agents:
            try:
                task = asyncio.wait_for(
                    agent.execute(user_input, shared_context),
                    timeout=self.timeout
                )
                tasks.append(task)
            except Exception as e:
                print(f"Error queuing agent {agent.name}: {e}")

        # Execute all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        aggregated = {
            "total_agents": len(agents),
            "successful": 0,
            "failed": 0,
            "results": []
        }

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                aggregated["failed"] += 1
                aggregated["results"].append({
                    "agent_id": agents[i].agent_id,
                    "status": "error",
                    "error": str(result)
                })
            else:
                aggregated["successful"] += 1
                aggregated["results"].append({
                    "agent_id": agents[i].agent_id,
                    "status": "success",
                    "result": result
                })

        return aggregated
