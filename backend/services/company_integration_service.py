"""
PHASE 4: 1000+ Company Integration
Company sync, agent mapping, integration registry
"""

from typing import List, Dict, Optional
import pandas as pd
import asyncio
from numpy import dot
from numpy.linalg import norm

class CompanySyncService:
    """Sync 1000+ companies from free data sources"""

    def __init__(self, db_session, ml_encoder):
        self.db = db_session
        self.encoder = ml_encoder  # sentence-transformers

    async def load_companies_from_csv(self, csv_path: str) -> int:
        """Load companies from free data source (Fortune 500, tech, etc)"""

        df = pd.read_csv(csv_path)
        count = 0

        for idx, row in df.iterrows():
            company = Company(
                name=row['name'],
                slug=self._slugify(row['name']),
                category=row.get('category', ''),
                industry=row.get('industry', ''),
                country=row.get('country', ''),
                website=row.get('website', ''),
                has_api=row.get('has_api', False),
                api_type=row.get('api_type', ''),
                logo_url=row.get('logo_url', ''),
                description=row.get('description', '')
            )

            self.db.add(company)
            count += 1

        self.db.commit()
        return count

    async def map_agents_to_companies(self) -> Dict:
        """
        Automatically map 1000 agents to 1000 companies
        Using semantic similarity (free sentence-transformers)
        """

        companies = self.db.query(Company).all()
        agents = self.db.query(AgentV2).filter(AgentV2.is_public == True).all()

        stats = {
            "total_mappings": 0,
            "high_confidence": 0,  # >0.8
            "medium_confidence": 0,  # 0.6-0.8
            "low_confidence": 0  # 0.4-0.6
        }

        for company in companies:
            # Company description for embedding
            company_text = f"{company.name} {company.category} {company.industry} {company.description}"
            company_embedding = self.encoder.encode(company_text)

            for agent in agents:
                # Agent description
                agent_text = f"{agent.name} {' '.join(agent.capabilities)}"
                agent_embedding = self.encoder.encode(agent_text)

                # Cosine similarity
                similarity = self._cosine_similarity(company_embedding, agent_embedding)

                # Map if confidence > 0.4
                if similarity > 0.4:
                    mapping = CompanyAgent(
                        company_id=company.id,
                        agent_id=agent.id,
                        confidence_score=similarity,
                        is_verified=similarity > 0.8
                    )

                    self.db.add(mapping)

                    stats["total_mappings"] += 1

                    if similarity > 0.8:
                        stats["high_confidence"] += 1
                    elif similarity > 0.6:
                        stats["medium_confidence"] += 1
                    else:
                        stats["low_confidence"] += 1

        self.db.commit()
        return stats

    async def get_agents_for_company(self, company_id: int, limit: int = 20) -> List[Dict]:
        """Get recommended agents for a company"""

        mappings = self.db.query(CompanyAgent).filter(
            CompanyAgent.company_id == company_id
        ).order_by(
            CompanyAgent.confidence_score.desc()
        ).limit(limit).all()

        agents = []
        for mapping in mappings:
            agent = self.db.query(AgentV2).get(mapping.agent_id)
            if agent:
                agents.append({
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "confidence": mapping.confidence_score,
                    "is_verified": mapping.is_verified
                })

        return agents

    def _slugify(self, text: str) -> str:
        """Convert text to slug"""

        return text.lower().replace(" ", "-").replace("_", "-")

    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between vectors"""

        try:
            return dot(vec1, vec2) / (norm(vec1) * norm(vec2))
        except:
            return 0.0


class IntegrationRegistryService:
    """Registry of API integrations per company"""

    # Free integrations available
    FREE_INTEGRATIONS = {
        "gmail": {
            "service": "Gmail",
            "auth_type": "oauth2",
            "api_type": "rest",
            "has_free_tier": True,
            "free_limit": "1M emails/day"
        },
        "slack": {
            "service": "Slack",
            "auth_type": "oauth2",
            "api_type": "rest",
            "has_free_tier": True,
            "free_limit": "90 days message history"
        },
        "telegram": {
            "service": "Telegram",
            "auth_type": "bot_token",
            "api_type": "rest",
            "has_free_tier": True,
            "free_limit": "Unlimited"
        },
        "github": {
            "service": "GitHub",
            "auth_type": "oauth2",
            "api_type": "rest/graphql",
            "has_free_tier": True,
            "free_limit": "60 req/hour"
        },
        "twitter": {
            "service": "Twitter/X",
            "auth_type": "oauth2",
            "api_type": "rest",
            "has_free_tier": True,
            "free_limit": "450 req/15min"
        },
        "discord": {
            "service": "Discord",
            "auth_type": "bot_token",
            "api_type": "rest",
            "has_free_tier": True,
            "free_limit": "Unlimited"
        },
        "stripe": {
            "service": "Stripe",
            "auth_type": "api_key",
            "api_type": "rest",
            "has_free_tier": True,
            "free_limit": "Test mode"
        },
        "aws_sns": {
            "service": "AWS SNS",
            "auth_type": "aws_credentials",
            "api_type": "rest",
            "has_free_tier": True,
            "free_limit": "100 SMS/month"
        }
    }

    def __init__(self, db_session):
        self.db = db_session

    async def register_integrations_for_company(self, company_id: int) -> List[Dict]:
        """Register available integrations for company"""

        registered = []

        for service_key, details in self.FREE_INTEGRATIONS.items():
            integration = CompanyIntegration(
                company_id=company_id,
                service_name=details["service"],
                auth_type=details["auth_type"],
                has_free_tier=details["has_free_tier"],
                free_tier_limits={"limit": details["free_limit"]}
            )

            self.db.add(integration)
            registered.append(details)

        self.db.commit()
        return registered

    async def get_integrations_for_company(self, company_id: int) -> List[Dict]:
        """Get all integrations for company"""

        integrations = self.db.query(CompanyIntegration).filter(
            CompanyIntegration.company_id == company_id
        ).all()

        return [
            {
                "service": i.service_name,
                "auth_type": i.auth_type,
                "has_free_tier": i.has_free_tier,
                "free_limits": i.free_tier_limits,
                "status": i.status
            }
            for i in integrations
        ]


class CompanyAnalyticsService:
    """Track company-agent usage and performance"""

    def __init__(self, db_session):
        self.db = db_session

    async def get_company_stats(self, company_id: int) -> Dict:
        """Get analytics for company"""

        company = self.db.query(Company).get(company_id)

        agent_mappings = self.db.query(CompanyAgent).filter(
            CompanyAgent.company_id == company_id
        ).count()

        verified_mappings = self.db.query(CompanyAgent).filter(
            CompanyAgent.company_id == company_id,
            CompanyAgent.is_verified == True
        ).count()

        return {
            "company_name": company.name,
            "total_agents_available": agent_mappings,
            "verified_agents": verified_mappings,
            "category": company.category,
            "has_api": company.has_api,
            "user_count": company.user_count,
            "average_agent_confidence": self._get_avg_confidence(company_id)
        }

    def _get_avg_confidence(self, company_id: int) -> float:
        """Calculate average agent confidence for company"""

        from sqlalchemy import func

        result = self.db.query(
            func.avg(CompanyAgent.confidence_score)
        ).filter(
            CompanyAgent.company_id == company_id
        ).scalar()

        return float(result or 0.0)
