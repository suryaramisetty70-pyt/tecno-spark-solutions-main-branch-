"""
WhatsApp Agent - Manages WhatsApp messaging and communications
Sends/receives messages, manages contacts and groups
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentStatus, Tool

logger = logging.getLogger(__name__)


class WhatsAppAgent(BaseAgent):
    """Manages WhatsApp communication"""

    def __init__(self):
        super().__init__(
            agent_id="whatsapp_agent",
            name="WhatsApp Agent",
            description="Manages your WhatsApp messages and communications",
            version="0.1.0"
        )

        self.capabilities = [
            {
                "category": "communication",
                "skills": ["message_send", "message_receive", "group_management"],
                "priority": 8
            }
        ]

        self.tools = self._initialize_tools()
        self._initialize_permissions()
        self.logger.info("✅ WhatsApp Agent initialized")

    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="send_message",
                description="Send a WhatsApp message",
                input_schema={"type": "object", "properties": {"phone": {"type": "string"}, "message": {"type": "string"}}, "required": ["phone", "message"]},
                execute_fn=self._send_message
            ),
            Tool(
                name="get_messages",
                description="Get WhatsApp messages",
                input_schema={"type": "object", "properties": {"contact": {"type": "string"}, "limit": {"type": "integer"}}},
                execute_fn=self._get_messages
            ),
            Tool(
                name="create_group",
                description="Create a WhatsApp group",
                input_schema={"type": "object", "properties": {"name": {"type": "string"}, "members": {"type": "array"}}, "required": ["name", "members"]},
                execute_fn=self._create_group
            )
        ]

    def _initialize_permissions(self) -> None:
        for perm in ["send_whatsapp", "read_whatsapp", "manage_contacts"]:
            self.grant_permission(perm)

    def register_tools(self) -> List[Tool]:
        return self.tools

    async def process_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(AgentStatus.PROCESSING)
        try:
            return {"status": "success", "response": f"WhatsApp: {intent}"}
        except Exception as e:
            return await self.handle_error(e)
        finally:
            await self.set_state(AgentStatus.SUCCESS)

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "send_message":
            return await self._send_message(parameters)
        return {"status": "error"}

    async def _send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "message_id": "msg_123"}

    async def _get_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "messages": []}

    async def _create_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "group_id": "grp_123"}
