"""Real Estate Agent - Property management and listings"""
from agents.base_agent import BaseAgent

class RealEstateAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="real_estate_agent", name="Real Estate Agent", description="Property management and real estate transactions")
        self.name = "Real Estate Agent"
        self.description = "Property management and real estate transactions"
        self.capabilities = ["list_property", "search_properties", "manage_tenants", "maintenance_requests", "valuation"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "list" in intent_lower or "sell" in intent_lower or "rent" in intent_lower: return {"action": "list_property", "confidence": 0.9}
        elif "search" in intent_lower or "find" in intent_lower: return {"action": "search_properties", "confidence": 0.85}
        elif "tenant" in intent_lower: return {"action": "manage_tenants", "confidence": 0.85}
        elif "maintenance" in intent_lower or "repair" in intent_lower: return {"action": "maintenance_requests", "confidence": 0.8}
        elif "value" in intent_lower or "price" in intent_lower: return {"action": "valuation", "confidence": 0.8}
        return {"action": "search_properties", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "list_property": return {"status": "success", "listing_id": "LST_123"}
        elif action == "search_properties": return {"status": "success", "properties_found": 45}
        elif action == "manage_tenants": return {"status": "success", "tenants_managed": 8}
        elif action == "maintenance_requests": return {"status": "success", "request_id": "MNT_001"}
        elif action == "valuation": return {"status": "success", "estimated_value": "$450,000"}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {
            "list_property": {"description": "List property", "required_params": ["address", "price"]},
            "search_properties": {"description": "Search properties", "required_params": ["location", "budget"]},
            "manage_tenants": {"description": "Manage tenants", "required_params": ["property_id"]},
            "maintenance_requests": {"description": "Request maintenance", "required_params": ["property_id", "issue_type"]},
            "valuation": {"description": "Get property valuation", "required_params": ["property_id"]},
        }
