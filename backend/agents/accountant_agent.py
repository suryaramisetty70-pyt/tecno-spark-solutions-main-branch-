"""
Accountant Agent - Manages expenses, invoices, and financial records
Tracks spending, generates reports, and assists with accounting
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentStatus, Tool

logger = logging.getLogger(__name__)


class AccountantAgent(BaseAgent):
    """Manages accounting and financial records"""

    def __init__(self):
        super().__init__(
            agent_id="accountant_agent",
            name="Accountant Agent",
            description="Manages your finances and accounting records",
            version="0.1.0"
        )

        self.capabilities = [
            {
                "category": "financial",
                "skills": ["expense_tracking", "financial_reporting", "reconciliation"],
                "priority": 8
            }
        ]

        self.tools = self._initialize_tools()
        self._initialize_permissions()
        self.logger.info("✅ Accountant Agent initialized")

    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="log_expense",
                description="Log an expense transaction",
                input_schema={"type": "object", "properties": {"amount": {"type": "number"}, "category": {"type": "string"}, "description": {"type": "string"}}, "required": ["amount", "category"]},
                execute_fn=self._log_expense
            ),
            Tool(
                name="create_invoice",
                description="Create an invoice",
                input_schema={"type": "object", "properties": {"client": {"type": "string"}, "amount": {"type": "number"}, "items": {"type": "array"}}, "required": ["client", "amount"]},
                execute_fn=self._create_invoice
            ),
            Tool(
                name="generate_report",
                description="Generate financial report",
                input_schema={"type": "object", "properties": {"period": {"type": "string"}, "report_type": {"type": "string"}}},
                execute_fn=self._generate_report
            )
        ]

    def _initialize_permissions(self) -> None:
        for perm in ["track_expenses", "manage_invoices", "access_financial_data"]:
            self.grant_permission(perm)

    def register_tools(self) -> List[Tool]:
        return self.tools

    async def process_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(AgentStatus.PROCESSING)
        try:
            return {"status": "success", "response": f"Accounting: {intent}"}
        except Exception as e:
            return await self.handle_error(e)
        finally:
            await self.set_state(AgentStatus.SUCCESS)

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "log_expense":
            return await self._log_expense(parameters)
        return {"status": "error"}

    async def _log_expense(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "expense_id": "exp_123"}

    async def _create_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "invoice_id": "inv_123"}

    async def _generate_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "report": {}}
