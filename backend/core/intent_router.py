"""
Intent Router - Analyzes user intent and routes to appropriate agent(s)
Core component of Buddy Core that understands what the user wants
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class IntentCategory(str, Enum):
    """Categories of user intents"""
    PRODUCTIVITY = "productivity"
    COMMUNICATION = "communication"
    RESEARCH = "research"
    LEARNING = "learning"
    FINANCIAL = "financial"
    BUSINESS = "business"
    TRAVEL = "travel"
    CONTENT = "content"
    PERSONAL = "personal"
    AUTOMATION = "automation"
    MEMORY = "memory"
    ANALYTICS = "analytics"
    ADMIN = "admin"
    OTHER = "other"


class IntentRouter:
    """
    Routes user intents to appropriate agents.
    Uses multiple strategies:
    1. Keyword-based matching (fast)
    2. Pattern matching (medium)
    3. NLP classification (when available)
    """

    def __init__(self):
        """Initialize intent router with rules and patterns"""
        self.logger = logging.getLogger(__name__)

        # Define intent patterns and their mapping to agents/categories
        self.intent_patterns = self._initialize_patterns()
        self.agent_capabilities = self._initialize_agent_capabilities()

    def _initialize_patterns(self) -> Dict[IntentCategory, List[Dict[str, Any]]]:
        """Initialize intent patterns for classification"""
        return {
            IntentCategory.PRODUCTIVITY: [
                {
                    "keywords": ["todo", "task", "reminder", "schedule", "deadline"],
                    "agents": ["productivity_agent", "scheduler_agent", "reminder_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.COMMUNICATION: [
                {
                    "keywords": ["email", "send", "message", "contact", "chat"],
                    "agents": ["email_agent", "whatsapp_agent", "telegram_agent", "linkedin_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.RESEARCH: [
                {
                    "keywords": ["research", "find", "search", "investigate", "look up"],
                    "agents": ["researcher_agent", "competitor_analysis_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.LEARNING: [
                {
                    "keywords": ["learn", "study", "course", "tutorial", "teach"],
                    "agents": ["student_agent", "teacher_agent", "tutor_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.FINANCIAL: [
                {
                    "keywords": ["expense", "invoice", "payment", "account", "balance", "tax"],
                    "agents": ["accountant_agent", "ca_agent", "banking_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.BUSINESS: [
                {
                    "keywords": ["sale", "deal", "lead", "customer", "report", "kpi"],
                    "agents": ["sales_agent", "ceo_agent", "business_analyst_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.TRAVEL: [
                {
                    "keywords": ["book", "flight", "hotel", "trip", "travel", "itinerary"],
                    "agents": ["booking_agent", "tourist_guide_agent", "trip_planner_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.CONTENT: [
                {
                    "keywords": ["write", "blog", "article", "content", "seo", "marketing"],
                    "agents": ["content_writer_agent", "seo_agent", "marketing_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.PERSONAL: [
                {
                    "keywords": ["note", "save", "remember", "personal", "private"],
                    "agents": ["memory_agent", "notes_agent", "personal_assistant_agent"],
                    "priority": "high"
                }
            ],
            IntentCategory.AUTOMATION: [
                {
                    "keywords": ["automate", "workflow", "trigger", "action", "if"],
                    "agents": ["automation_agent", "workflow_engine"],
                    "priority": "high"
                }
            ],
            IntentCategory.ANALYTICS: [
                {
                    "keywords": ["metric", "statistic", "dashboard", "report", "analytics"],
                    "agents": ["analytics_agent", "business_analyst_agent"],
                    "priority": "medium"
                }
            ]
        }

    def _initialize_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Define what each agent can do by dynamically loading from agent configs."""
        import json
        from pathlib import Path
        import os
        
        capabilities = {
            "personal_assistant_agent": {
                "category": IntentCategory.PERSONAL,
                "skills": ["coordination", "general_assistance", "routing"],
                "priority": 10
            }
        }
        
        # Determine paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        agents_dir = os.path.join(base_dir, "agents")
        
        if os.path.exists(agents_dir):
            for filename in os.listdir(agents_dir):
                if filename.endswith("_config.json"):
                    try:
                        filepath = os.path.join(agents_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Try to map category
                        cat_str = (data.get("category") or "business").upper()
                        category_enum = IntentCategory.OTHER
                        for enum_member in IntentCategory:
                            if enum_member.name == cat_str:
                                category_enum = enum_member
                                break
                        
                        agent_id = data.get("name", "").lower().replace(" ", "_")
                        if agent_id:
                            capabilities[agent_id] = {
                                "category": category_enum,
                                "skills": data.get("capabilities", []),
                                "priority": 5
                            }
                    except Exception as e:
                        self.logger.warning(f"Failed to load agent config {filename}: {e}")
                        
        return capabilities

    async def classify_intent(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> Tuple[IntentCategory, float]:
        """
        Classify user intent into category.

        Args:
            user_message: User's input message
            context: Additional context

        Returns:
            Tuple of (category, confidence_score)
        """
        message_lower = user_message.lower()

        # Score each category
        category_scores = {}

        for category, patterns in self.intent_patterns.items():
            score = 0.0

            for pattern in patterns:
                keywords = pattern.get("keywords", [])
                # Check for keyword matches
                matches = sum(1 for kw in keywords if kw in message_lower)
                score += matches * 0.25  # Each keyword match adds 0.25

            category_scores[category] = min(score, 1.0)  # Cap at 1.0

        # Get highest scoring category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
        else:
            best_category = IntentCategory.OTHER
            confidence = 0.0

        self.logger.info(
            f"Intent classified: {best_category.value} "
            f"(confidence: {confidence:.2f})"
        )

        return best_category, confidence

    async def select_agents(
        self,
        category: IntentCategory,
        context: Dict[str, Any]
    ) -> List[Tuple[str, float, int]]:
        """
        Select appropriate agents for handling intent.

        Args:
            category: Intent category
            context: Additional context

        Returns:
            List of (agent_id, capability_score, priority) tuples
        """
        selected_agents = []

        # Get agents for this category
        for agent_id, agent_info in self.agent_capabilities.items():
            if agent_info.get("category") == category:
                capability_score = 0.8  # Base score
                priority = agent_info.get("priority", 5)
                selected_agents.append((agent_id, capability_score, priority))

        # Sort by priority (highest first)
        selected_agents.sort(key=lambda x: x[2], reverse=True)

        self.logger.info(
            f"Selected {len(selected_agents)} agents for {category.value}"
        )

        return selected_agents

    async def route(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete routing process.

        Args:
            user_message: User's message
            context: Additional context

        Returns:
            Routing decision with selected agents and metadata
        """
        start_time = datetime.now()

        # Classify intent
        category, confidence = await self.classify_intent(user_message, context)

        # Select agents
        agents = await self.select_agents(category, context)

        processing_time = (datetime.now() - start_time).total_seconds()

        routing_decision = {
            "category": category.value,
            "confidence": confidence,
            "agents": [
                {
                    "agent_id": agent_id,
                    "capability_score": score,
                    "priority": priority
                }
                for agent_id, score, priority in agents
            ],
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }

        self.logger.info(
            f"Routing decision made in {processing_time:.3f}s: "
            f"{len(agents)} agents selected"
        )

        return routing_decision

    def add_agent_capability(
        self,
        agent_id: str,
        category: IntentCategory,
        skills: List[str],
        priority: int = 5
    ) -> None:
        """
        Register new agent capability.

        Args:
            agent_id: Agent identifier
            category: Intent category
            skills: List of skills
            priority: Priority level
        """
        self.agent_capabilities[agent_id] = {
            "category": category,
            "skills": skills,
            "priority": priority
        }
        self.logger.info(f"Agent capability registered: {agent_id}")

    def get_router_stats(self) -> Dict[str, Any]:
        """Get router statistics"""
        return {
            "total_agents": len(self.agent_capabilities),
            "categories": len(self.intent_patterns),
            "patterns": sum(
                len(patterns)
                for patterns in self.intent_patterns.values()
            )
        }
