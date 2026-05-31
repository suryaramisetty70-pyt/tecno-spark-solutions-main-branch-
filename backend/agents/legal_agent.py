"""Legal Agent - Legal document and compliance management"""
from backend.agents.base_agent import BaseAgent

class LegalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Legal Agent"
        self.description = "Legal document review and compliance management"
        self.capabilities = ["review_contracts", "manage_compliance", "generate_documents", "track_deadlines", "risk_assessment"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "contract" in intent_lower or "agreement" in intent_lower: return {"action": "review_contracts", "confidence": 0.9}
        elif "compliance" in intent_lower or "regulation" in intent_lower: return {"action": "manage_compliance", "confidence": 0.85}
        elif "document" in intent_lower: return {"action": "generate_documents", "confidence": 0.85}
        elif "deadline" in intent_lower: return {"action": "track_deadlines", "confidence": 0.8}
        elif "risk" in intent_lower: return {"action": "risk_assessment", "confidence": 0.8}
        return {"action": "generate_documents", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "review_contracts": return {"status": "success", "risk_level": "low", "notes": "All clear"}
        elif action == "manage_compliance": return {"status": "success", "compliant": True}
        elif action == "generate_documents": return {"status": "success", "document_id": "DOC_789"}
        elif action == "track_deadlines": return {"status": "success", "upcoming_deadlines": 3}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {
            "review_contracts": {"description": "Review contracts", "required_params": ["contract_id"]},
            "manage_compliance": {"description": "Manage compliance", "required_params": ["jurisdiction"]},
            "generate_documents": {"description": "Generate legal documents", "required_params": ["document_type"]},
            "track_deadlines": {"description": "Track legal deadlines", "required_params": ["case_id"]},
            "risk_assessment": {"description": "Assess legal risk", "required_params": ["scenario"]},
        }
