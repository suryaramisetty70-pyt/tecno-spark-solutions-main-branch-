"""Medical Agent - Healthcare and appointment management"""
from backend.agents.base_agent import BaseAgent

class MedicalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Medical Agent"
        self.description = "Healthcare records and appointment management"
        self.capabilities = ["manage_appointments", "track_health", "medication_reminders", "medical_records", "symptom_checker"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "appointment" in intent_lower: return {"action": "manage_appointments", "confidence": 0.9}
        elif "health" in intent_lower or "blood" in intent_lower: return {"action": "track_health", "confidence": 0.85}
        elif "medication" in intent_lower or "medicine" in intent_lower: return {"action": "medication_reminders", "confidence": 0.9}
        elif "record" in intent_lower or "history" in intent_lower: return {"action": "medical_records", "confidence": 0.85}
        elif "symptom" in intent_lower: return {"action": "symptom_checker", "confidence": 0.8}
        return {"action": "manage_appointments", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "manage_appointments": return {"status": "success", "appointment_id": "APT_001"}
        elif action == "track_health": return {"status": "success", "bmi": 23.5, "status": "healthy"}
        elif action == "medication_reminders": return {"status": "success", "reminders_set": 4}
        elif action == "medical_records": return {"status": "success", "records_count": 15}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {
            "manage_appointments": {"description": "Manage appointments", "required_params": ["doctor_id", "date"]},
            "track_health": {"description": "Track health metrics", "required_params": ["metric_type"]},
            "medication_reminders": {"description": "Set medication reminders", "required_params": ["medication", "frequency"]},
            "medical_records": {"description": "Access medical records", "required_params": ["record_type"]},
            "symptom_checker": {"description": "Check symptoms", "required_params": ["symptoms"]},
        }
