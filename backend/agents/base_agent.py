"""
Base Agent Class - Foundation for all AI agents in Buddy AI OS
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    EXECUTING = "executing"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class Tool:
    """Tool definition for agent usage"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    execute_fn: Any  # Callable function


@dataclass
class AgentState:
    """Agent execution state"""
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    last_executed: Optional[datetime] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in Buddy AI OS.
    Every agent inherits from this class and implements core methods.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        version: str = "0.1.0"
    ):
        """Initialize base agent"""
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.version = version
        self.state = AgentState()
        self.tools: List[Tool] = []
        self.memory: Dict[str, Any] = {}
        self.permissions: List[str] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def process_intent(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user intent and return response.

        Args:
            intent: User's intention/command
            context: Contextual information (conversation history, user data, etc)

        Returns:
            Dictionary with action, parameters, and result
        """
        pass

    @abstractmethod
    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute specific action requested by another agent or user.

        Args:
            action: Action name
            parameters: Action parameters

        Returns:
            Dictionary with execution result
        """
        pass

    @abstractmethod
    def register_tools(self) -> List[Tool]:
        """
        Register tools that this agent provides to other agents.

        Returns:
            List of Tool objects this agent provides
        """
        pass

    def validate_permissions(self, permission: str) -> bool:
        """
        Check if agent has permission for specific action.

        Args:
            permission: Permission to check

        Returns:
            True if permission granted
        """
        return permission in self.permissions

    def grant_permission(self, permission: str) -> None:
        """Grant permission to agent"""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.logger.info(f"Permission granted: {permission}")

    def revoke_permission(self, permission: str) -> None:
        """Revoke permission from agent"""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.logger.info(f"Permission revoked: {permission}")

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors that occur during execution.

        Args:
            error: Exception that occurred

        Returns:
            Dictionary with error information
        """
        self.state.status = AgentStatus.ERROR
        self.state.error_message = str(error)
        self.logger.error(f"Error in {self.name}: {error}", exc_info=True)

        return {
            "status": "error",
            "agent": self.name,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        }

    def save_memory(self, key: str, value: Any) -> None:
        """Save agent-specific memory"""
        self.memory[key] = value
        self.logger.debug(f"Memory saved: {key}")

    def get_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve agent-specific memory"""
        return self.memory.get(key, default)

    def clear_memory(self) -> None:
        """Clear agent memory"""
        self.memory.clear()
        self.logger.info("Memory cleared")

    async def notify_other_agents(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Notify other agents about important events.
        This will be connected to the Event Bus.

        Args:
            event_type: Type of event
            event_data: Event data
        """
        self.logger.info(f"Event notification: {event_type}")
        # TODO: Connect to Event Bus

    def get_state(self) -> AgentState:
        """Get current agent state"""
        return self.state

    async def set_state(self, status: AgentStatus, **kwargs) -> None:
        """Update agent state"""
        self.state.status = status
        self.state.last_executed = datetime.now()

        for key, value in kwargs.items():
            setattr(self.state, key, value)

        self.logger.debug(f"State updated: {status}")

    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.state.status.value,
            "tools": len(self.tools),
            "permissions": self.permissions
        }

    async def __call__(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make agent callable for processing intents.
        Entry point for processing.
        """
        try:
            await self.set_state(AgentStatus.PROCESSING)
            result = await self.process_intent(intent, context)
            await self.set_state(AgentStatus.SUCCESS)
            return result
        except Exception as e:
            return await self.handle_error(e)
