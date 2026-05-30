"""
Memory Engine - Manages short-term and long-term memory for the system
Stores user context, agent knowledge, and past interactions
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of memories in the system"""
    CONVERSATION = "conversation"
    NOTE = "note"
    DOCUMENT = "document"
    INSTRUCTION = "instruction"
    PREFERENCE = "preference"
    GOAL = "goal"
    CONTACT = "contact"
    EVENT = "event"
    FACT = "fact"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    CUSTOM = "custom"


@dataclass
class Memory:
    """Represents a single memory item"""
    memory_id: str
    user_id: str
    memory_type: MemoryType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    importance: int = field(default=5)  # 1-10, higher = more important

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary"""
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "tags": self.tags,
            "importance": self.importance
        }


@dataclass
class ShortTermMemory:
    """Short-term context for current session"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    active_agents: List[str] = field(default_factory=list)
    active_workflow: Optional[str] = None
    current_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    max_history: int = 50

    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only recent messages
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

        self.last_updated = datetime.now()

    def get_recent_context(self, num_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context"""
        return self.conversation_history[-num_messages:]

    def clear(self) -> None:
        """Clear short-term memory"""
        self.conversation_history.clear()
        self.active_agents.clear()
        self.active_workflow = None
        self.current_context.clear()


class MemoryEngine:
    """
    Manages both short-term and long-term memory for the system.
    Short-term: Session context, active conversations
    Long-term: Persistent user data, preferences, history
    """

    def __init__(self):
        """Initialize memory engine"""
        self.logger = logging.getLogger(__name__)

        # Short-term memory storage (in-memory)
        self.short_term: Dict[str, ShortTermMemory] = {}

        # Long-term memory storage (would be backed by PostgreSQL + ChromaDB)
        self.long_term: Dict[str, List[Memory]] = {}

        # User metadata
        self.user_metadata: Dict[str, Dict[str, Any]] = {}

        self.logger.info("✅ Memory Engine initialized")

    async def create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create new short-term memory session.

        Args:
            user_id: User ID
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            Session ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        self.short_term[session_id] = ShortTermMemory(
            user_id=user_id,
            session_id=session_id
        )

        self.logger.info(f"Session created: {session_id}")
        return session_id

    async def save_memory(
        self,
        user_id: str,
        memory_type: MemoryType,
        content: str,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None,
        importance: int = 5
    ) -> str:
        """
        Save to long-term memory.

        Args:
            user_id: User ID
            memory_type: Type of memory
            content: Memory content
            metadata: Additional metadata
            tags: Search tags
            importance: Importance level

        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())

        memory = Memory(
            memory_id=memory_id,
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            metadata=metadata or {},
            tags=tags or [],
            importance=importance
        )

        # Store memory
        if user_id not in self.long_term:
            self.long_term[user_id] = []

        self.long_term[user_id].append(memory)

        self.logger.info(
            f"Memory saved: {memory_type.value} ({len(content)} chars)"
        )

        return memory_id

    async def retrieve_memory(
        self,
        user_id: str,
        query: str,
        memory_type: Optional[MemoryType] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories matching query.

        Args:
            user_id: User ID
            query: Search query
            memory_type: Optional filter by type
            top_k: Number of results

        Returns:
            List of matching memories
        """
        if user_id not in self.long_term:
            return []

        memories = self.long_term[user_id]

        # Filter by type if specified
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        # Simple keyword matching (would use semantic search with embeddings in production)
        query_lower = query.lower()
        scored_memories = []

        for memory in memories:
            # Score based on keyword matches
            score = 0
            if query_lower in memory.content.lower():
                score += 1
            for tag in memory.tags:
                if query_lower in tag.lower():
                    score += 1
            if score > 0:
                scored_memories.append((memory, score))

        # Sort by score and importance
        scored_memories.sort(
            key=lambda x: (x[1], x[0].importance),
            reverse=True
        )

        # Update access count and return
        results = []
        for memory, _ in scored_memories[:top_k]:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            results.append(memory.to_dict())

        self.logger.info(
            f"Retrieved {len(results)} memories for query: {query}"
        )

        return results

    async def add_to_conversation(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Add message to short-term conversation memory.

        Args:
            session_id: Session ID
            role: Message role (user/assistant/agent)
            content: Message content
        """
        if session_id in self.short_term:
            self.short_term[session_id].add_message(role, content)

    async def get_session_context(
        self,
        session_id: str,
        num_messages: int = 10
    ) -> Dict[str, Any]:
        """
        Get current session context.

        Args:
            session_id: Session ID
            num_messages: Number of recent messages

        Returns:
            Session context
        """
        if session_id not in self.short_term:
            return {}

        session = self.short_term[session_id]
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "conversation": session.get_recent_context(num_messages),
            "active_agents": session.active_agents,
            "active_workflow": session.active_workflow,
            "context": session.current_context,
            "created_at": session.created_at.isoformat(),
            "last_updated": session.last_updated.isoformat()
        }

    async def update_session_context(
        self,
        session_id: str,
        context_update: Dict[str, Any]
    ) -> None:
        """
        Update session context.

        Args:
            session_id: Session ID
            context_update: Context updates
        """
        if session_id in self.short_term:
            session = self.short_term[session_id]
            session.current_context.update(context_update)
            session.last_updated = datetime.now()

    async def get_user_memories(
        self,
        user_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all user memories.

        Args:
            user_id: User ID
            memory_type: Optional filter by type
            limit: Maximum number to return

        Returns:
            List of memories
        """
        if user_id not in self.long_term:
            return []

        memories = self.long_term[user_id]

        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        # Return most recent
        return [m.to_dict() for m in memories[-limit:]]

    def get_memory_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get memory statistics"""
        if user_id:
            user_memories = self.long_term.get(user_id, [])
            return {
                "user_id": user_id,
                "long_term_memories": len(user_memories),
                "by_type": {
                    mt.value: len([m for m in user_memories if m.memory_type == mt])
                    for mt in MemoryType
                }
            }

        return {
            "total_users": len(self.long_term),
            "total_long_term_memories": sum(
                len(mems) for mems in self.long_term.values()
            ),
            "total_sessions": len(self.short_term)
        }

    async def clear_session(self, session_id: str) -> None:
        """Clear session"""
        if session_id in self.short_term:
            del self.short_term[session_id]
            self.logger.info(f"Session cleared: {session_id}")
