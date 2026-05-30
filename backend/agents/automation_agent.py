"""
Automation Agent - Creates and manages automated workflows
Enables users to create complex automations without coding
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentStatus, Tool

logger = logging.getLogger(__name__)


class AutomationAgent(BaseAgent):
    """Creates and manages automated workflows"""

    def __init__(self):
        super().__init__(
            agent_id="automation_agent",
            name="Automation Agent",
            description="Creates and manages automated workflows",
            version="0.1.0"
        )

        self.capabilities = [
            {
                "category": "automation",
                "skills": ["workflow_creation", "trigger_definition", "action_execution"],
                "priority": 9
            }
        ]

        self.tools = self._initialize_tools()
        self._initialize_permissions()
        self.logger.info("✅ Automation Agent initialized")

    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="create_workflow",
                description="Create a new automation workflow",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "triggers": {"type": "array"},
                        "actions": {"type": "array"},
                        "condition": {"type": "string"}
                    },
                    "required": ["name", "triggers", "actions"]
                },
                execute_fn=self._create_workflow
            ),
            Tool(
                name="set_trigger",
                description="Set trigger for automation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "trigger_type": {"type": "string"},
                        "condition": {"type": "string"}
                    },
                    "required": ["trigger_type"]
                },
                execute_fn=self._set_trigger
            ),
            Tool(
                name="execute_workflow",
                description="Manually execute a workflow",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"}
                    },
                    "required": ["workflow_id"]
                },
                execute_fn=self._execute_workflow
            )
        ]

    def _initialize_permissions(self) -> None:
        for perm in ["create_workflow", "execute_workflow", "manage_triggers", "manage_actions"]:
            self.grant_permission(perm)

    def register_tools(self) -> List[Tool]:
        return self.tools

    async def process_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(AgentStatus.PROCESSING)
        try:
            intent_lower = intent.lower()
            if any(w in intent_lower for w in ["automate", "workflow", "create automation"]):
                return {
                    "status": "success",
                    "action": "create_workflow",
                    "response": "I can help you automate that. What would you like to automate?"
                }
            return {"status": "success", "response": f"Automation: {intent}"}
        except Exception as e:
            return await self.handle_error(e)
        finally:
            await self.set_state(AgentStatus.SUCCESS)

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "create_workflow":
            return await self._create_workflow(parameters)
        return {"status": "error", "error": f"Unknown action: {action}"}

    async def _create_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "workflow_id": "workflow_123",
            "name": params.get("name"),
            "created_at": datetime.now().isoformat()
        }

    async def _set_trigger(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "trigger_set": True}

    async def _execute_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "workflow_executed": True}
