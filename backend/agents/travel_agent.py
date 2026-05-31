"""Travel Agent - Trip planning and booking"""
from backend.agents.base_agent import BaseAgent

class TravelAgentImpl(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Travel Agent"
        self.description = "Travel planning, bookings, and itinerary management"
        self.capabilities = ["search_flights", "book_hotel", "plan_itinerary", "travel_alerts", "currency_exchange"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "flight" in intent_lower: return {"action": "search_flights", "confidence": 0.9}
        elif "hotel" in intent_lower or "accommodation" in intent_lower: return {"action": "book_hotel", "confidence": 0.85}
        elif "itinerary" in intent_lower or "plan" in intent_lower: return {"action": "plan_itinerary", "confidence": 0.85}
        elif "alert" in intent_lower or "price" in intent_lower: return {"action": "travel_alerts", "confidence": 0.8}
        elif "exchange" in intent_lower or "currency" in intent_lower: return {"action": "currency_exchange", "confidence": 0.8}
        return {"action": "search_flights", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "search_flights": return {"status": "success", "flights_found": 25, "best_price": "$350"}
        elif action == "book_hotel": return {"status": "success", "booking_id": "HTL_789"}
        elif action == "plan_itinerary": return {"status": "success", "itinerary_id": "ITN_456"}
        elif action == "travel_alerts": return {"status": "success", "alerts_set": 3}
        elif action == "currency_exchange": return {"status": "success", "rate": 1.15}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {
            "search_flights": {"description": "Search flights", "required_params": ["from_city", "to_city", "date"]},
            "book_hotel": {"description": "Book hotel", "required_params": ["city", "check_in", "check_out"]},
            "plan_itinerary": {"description": "Plan trip", "required_params": ["destinations", "duration"]},
            "travel_alerts": {"description": "Set price alerts", "required_params": ["route", "max_price"]},
            "currency_exchange": {"description": "Check exchange rates", "required_params": ["from_currency", "to_currency"]},
        }
