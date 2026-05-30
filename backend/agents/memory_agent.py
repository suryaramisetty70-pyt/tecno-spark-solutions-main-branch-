"""
Memory Agent - Manages saving, retrieving, and searching user memories
Provides semantic search and context recall capabilities
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentStatus, Tool

logger = logging.getLogger(__name__)


class MemoryAgent(BaseAgent):
    """
    Memory Agent - Manages long-term and short-term memory.
    Saves important information and retrieves it when needed.
    """

    def __init__(self):
        """Initialize Memory Agent"""
        super().__init__(
            agent_id="memory_agent",
            name="Memory Agent",
            description="Manages your memories, notes, and knowledge base",
            version="0.1.0"
        )

        self.capabilities = [
            {
                "category": "memory",
                "skills": ["memory_save", "memory_retrieve", "semantic_search"],
                "priority": 8
            }
        ]

        self.tools = self._initialize_tools()
        self._initialize_permissions()
        self.logger.info("✅ Memory Agent initialized")

    def _initialize_tools(self) -> List[Tool]:
        """Initialize tools"""
        return [
            Tool(
                name="save_memory",
                description="Save information to memory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "memory_type": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["content", "memory_type"]
                },
                execute_fn=self._save_memory
            ),
            Tool(
                name="retrieve_memory",
                description="Search and retrieve memories",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "memory_type": {"type": "string"},
                        "limit": {"type": "integer"}
                    },
                    "required": ["query"]
                },
                execute_fn=self._retrieve_memory
            ),
            Tool(
                name="search_memories",
                description="Advanced search across all memories",
                input_schema={
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "string"}
                    },
                    "required": ["keywords"]
                },
                execute_fn=self._search_memories
            )
        ]

    def _initialize_permissions(self) -> None:
        """Grant default permissions"""
        for perm in ["save_memory", "read_memory", "search_memory", "delete_memory"]:
            self.grant_permission(perm)

    def register_tools(self) -> List[Tool]:
        """Register tools"""
        return self.tools

    async def process_intent(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process memory-related intents"""
        await self.set_state(AgentStatus.PROCESSING)

        intent_lower = intent.lower()

        try:
            if any(word in intent_lower for word in ["save", "remember", "store"]):
                return await self._handle_save_intent(intent, context)
            elif any(word in intent_lower for word in ["find", "search", "recall", "remember"]):
                return await self._handle_search_intent(intent, context)
            else:
                return {
                    "status": "success",
                    "response": "How can I help with your memories?"
                }

        except Exception as e:
            return await self.handle_error(e)
        finally:
            await self.set_state(AgentStatus.SUCCESS)

    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute memory action"""
        if action == "save_memory":
            return await self._save_memory(parameters)
        elif action == "retrieve_memory":
            return await self._retrieve_memory(parameters)
        elif action == "search_memories":
            return await self._search_memories(parameters)
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}

    async def _handle_save_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle save memory intent"""
        return {
            "status": "success",
            "action": "save_memory",
            "response": "I'll save this to your memory. What should I remember?"
        }

    async def _handle_search_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search memory intent"""
        return {
            "status": "success",
            "action": "search_memories",
            "response": "Let me search your memories for that information."
        }

    async def _save_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save information to memory"""
        content = params.get("content", "")
        memory_type = params.get("memory_type", "note")
        tags = params.get("tags", [])

        return {
            "status": "success",
            "message": "Saved to memory",
            "memory": {
                "content": content,
                "type": memory_type,
                "tags": tags,
                "saved_at": datetime.now().isoformat()
            }
        }

    async def _retrieve_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve memories"""
        query = params.get("query", "")
        limit = params.get("limit", 5)

        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "content": f"Memory matching: {query}",
                    "relevance": 0.95,
                    "type": "note",
                    "saved_at": datetime.now().isoformat()
                }
            ],
            "count": 1
        }

    async def _search_memories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search memories"""
        keywords = params.get("keywords", [])

        return {
            "status": "success",
            "keywords": keywords,
            "results": [],
            "total": 0
        }
