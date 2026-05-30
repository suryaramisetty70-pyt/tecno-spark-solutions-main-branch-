"""
Personal Assistant Agent - Main AI orchestrator
Handles general assistance, task coordination, and user intent routing
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentStatus, Tool

logger = logging.getLogger(__name__)


class PersonalAssistantAgent(BaseAgent):
    """
    Personal Assistant Agent - The main interface for user interactions.
    Understands natural language, coordinates other agents, and manages user assistance.
    """

    def __init__(self):
        """Initialize Personal Assistant Agent"""
        super().__init__(
            agent_id="personal_assistant",
            name="Personal Assistant",
            description="Your AI personal assistant for general tasks and coordination",
            version="0.1.0"
        )

        # Register capabilities
        self.capabilities = [
            {
                "category": "personal",
                "skills": ["coordination", "general_assistance", "task_routing"],
                "priority": 10
            }
        ]

        # Define tools this agent provides
        self.tools = self._initialize_tools()

        # Grant default permissions
        self._initialize_permissions()

        self.logger.info("✅ Personal Assistant Agent initialized")

    def _initialize_tools(self) -> List[Tool]:
        """Initialize tools for this agent"""
        tools = []

        # Tool 1: Get help on any topic
        tools.append(Tool(
            name="get_help",
            description="Get help on any topic from the AI system",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to get help on"},
                    "detail_level": {"type": "string", "enum": ["brief", "detailed"]}
                },
                "required": ["topic"]
            },
            execute_fn=self._get_help
        ))

        # Tool 2: Create task
        tools.append(Tool(
            name="create_task",
            description="Create a new task",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "due_date": {"type": "string"}
                },
                "required": ["title"]
            },
            execute_fn=self._create_task
        ))

        # Tool 3: Set reminder
        tools.append(Tool(
            name="set_reminder",
            description="Set a reminder for a task or event",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "time": {"type": "string"},
                    "type": {"type": "string", "enum": ["one_time", "recurring"]}
                },
                "required": ["title", "time"]
            },
            execute_fn=self._set_reminder
        ))

        return tools

    def _initialize_permissions(self) -> None:
        """Grant default permissions"""
        permissions = [
            "read_user_profile",
            "create_tasks",
            "set_reminders",
            "coordinate_agents",
            "access_memory",
            "view_workflows",
            "execute_workflows"
        ]

        for perm in permissions:
            self.grant_permission(perm)

    def register_tools(self) -> List[Tool]:
        """Register tools provided by this agent"""
        return self.tools

    async def process_intent(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user intent.

        Args:
            intent: User's intention/command
            context: Contextual information

        Returns:
            Response to user
        """
        await self.set_state(AgentStatus.PROCESSING)

        self.logger.info(f"Personal Assistant processing: {intent[:50]}...")

        try:
            # Parse intent to determine what to do
            intent_lower = intent.lower()

            # Handle specific intent patterns
            if any(word in intent_lower for word in ["create", "add", "new"]) and "task" in intent_lower:
                return await self._handle_create_task(intent, context)

            elif any(word in intent_lower for word in ["remind", "reminder", "set"]) and "remind" in intent_lower:
                return await self._handle_set_reminder(intent, context)

            elif any(word in intent_lower for word in ["help", "how", "what", "tell"]):
                return await self._handle_help(intent, context)

            else:
                # General response
                return {
                    "status": "success",
                    "response": f"I understand you want to: {intent}. Let me coordinate the right agents for this.",
                    "next_action": "route_to_specialized_agent",
                    "context": context
                }

        except Exception as e:
            self.logger.error(f"Error processing intent: {e}", exc_info=True)
            return await self.handle_error(e)

        finally:
            await self.set_state(AgentStatus.SUCCESS)

    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute specific action.

        Args:
            action: Action name
            parameters: Action parameters

        Returns:
            Action result
        """
        self.logger.info(f"Personal Assistant executing action: {action}")

        if not self.validate_permissions(f"execute_{action}"):
            return {
                "status": "error",
                "error": f"Permission denied: {action}"
            }

        try:
            if action == "help":
                return await self._get_help(parameters)

            elif action == "create_task":
                return await self._create_task(parameters)

            elif action == "set_reminder":
                return await self._set_reminder(parameters)

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    # Internal handler methods
    async def _handle_create_task(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle task creation intent"""
        return {
            "status": "success",
            "action": "create_task",
            "response": "I'll create a task for you. Please provide the task details.",
            "required_info": ["title", "priority", "due_date"],
            "intent": intent
        }

    async def _handle_set_reminder(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle reminder setting intent"""
        return {
            "status": "success",
            "action": "set_reminder",
            "response": "I'll set a reminder for you. When do you want to be reminded?",
            "required_info": ["time", "title"],
            "intent": intent
        }

    async def _handle_help(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle help request"""
        return {
            "status": "success",
            "action": "provide_help",
            "response": "I'm here to help! I can assist with tasks, reminders, email, research, and much more. What would you like help with?",
            "capabilities": [
                "Task management",
                "Reminders and scheduling",
                "Email management",
                "Research and information lookup",
                "Workflow automation",
                "Document management"
            ]
        }

    async def _get_help(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get help on a topic"""
        topic = params.get("topic", "")
        detail_level = params.get("detail_level", "brief")

        return {
            "status": "success",
            "topic": topic,
            "detail_level": detail_level,
            "help_content": f"Help on {topic}...",
            "timestamp": datetime.now().isoformat()
        }

    async def _create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task"""
        title = params.get("title", "Untitled Task")
        description = params.get("description", "")
        priority = params.get("priority", "medium")
        due_date = params.get("due_date")

        return {
            "status": "success",
            "action": "create_task",
            "task": {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
                "created_at": datetime.now().isoformat()
            }
        }

    async def _set_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set a reminder"""
        title = params.get("title", "Reminder")
        time = params.get("time")
        reminder_type = params.get("type", "one_time")

        return {
            "status": "success",
            "action": "set_reminder",
            "reminder": {
                "title": title,
                "time": time,
                "type": reminder_type,
                "created_at": datetime.now().isoformat()
            }
        }
