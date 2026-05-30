"""
Booking Agent - Manages reservations for flights, hotels, restaurants
Handles travel and hospitality bookings
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentStatus, Tool

logger = logging.getLogger(__name__)


class BookingAgent(BaseAgent):
    """Manages travel and hospitality bookings"""

    def __init__(self):
        super().__init__(
            agent_id="booking_agent",
            name="Booking Agent",
            description="Books flights, hotels, restaurants, and travel",
            version="0.1.0"
        )

        self.capabilities = [
            {
                "category": "travel",
                "skills": ["flight_booking", "hotel_booking", "restaurant_booking"],
                "priority": 7
            }
        ]

        self.tools = self._initialize_tools()
        self._initialize_permissions()
        self.logger.info("✅ Booking Agent initialized")

    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="book_flight",
                description="Book a flight",
                input_schema={"type": "object", "properties": {"from": {"type": "string"}, "to": {"type": "string"}, "date": {"type": "string"}}, "required": ["from", "to", "date"]},
                execute_fn=self._book_flight
            ),
            Tool(
                name="book_hotel",
                description="Book a hotel",
                input_schema={"type": "object", "properties": {"city": {"type": "string"}, "check_in": {"type": "string"}, "nights": {"type": "integer"}}, "required": ["city", "check_in", "nights"]},
                execute_fn=self._book_hotel
            ),
            Tool(
                name="book_restaurant",
                description="Book a restaurant",
                input_schema={"type": "object", "properties": {"restaurant": {"type": "string"}, "date": {"type": "string"}, "guests": {"type": "integer"}}, "required": ["restaurant", "date"]},
                execute_fn=self._book_restaurant
            )
        ]

    def _initialize_permissions(self) -> None:
        for perm in ["book_flights", "book_hotels", "book_restaurants"]:
            self.grant_permission(perm)

    def register_tools(self) -> List[Tool]:
        return self.tools

    async def process_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(AgentStatus.PROCESSING)
        try:
            return {"status": "success", "response": f"Booking: {intent}"}
        except Exception as e:
            return await self.handle_error(e)
        finally:
            await self.set_state(AgentStatus.SUCCESS)

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "book_flight":
            return await self._book_flight(parameters)
        return {"status": "error"}

    async def _book_flight(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "booking_id": "booking_123"}

    async def _book_hotel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "booking_id": "booking_124"}

    async def _book_restaurant(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "booking_id": "booking_125"}
