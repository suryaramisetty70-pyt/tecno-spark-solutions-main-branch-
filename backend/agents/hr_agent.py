"""HR Agent - Human resources and employee management"""
from backend.agents.base_agent import BaseAgent

class HRAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "HR Agent"
        self.description = "Human resources and employee management"
        self.capabilities = ["manage_employees", "process_payroll", "track_attendance", "manage_benefits", "recruitment"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "payroll" in intent_lower or "salary" in intent_lower: return {"action": "process_payroll", "confidence": 0.9}
        elif "attendance" in intent_lower or "leaves" in intent_lower: return {"action": "track_attendance", "confidence": 0.85}
        elif "benefit" in intent_lower: return {"action": "manage_benefits", "confidence": 0.85}
        elif "hire" in intent_lower or "recruit" in intent_lower: return {"action": "recruitment", "confidence": 0.8}
        return {"action": "manage_employees", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "process_payroll": return {"status": "success", "payroll_id": "PR_2024_001"}
        elif action == "track_attendance": return {"status": "success", "records_updated": 45}
        elif action == "manage_benefits": return {"status": "success", "benefits_configured": True}
        elif action == "recruitment": return {"status": "success", "job_posted": True, "candidates": 12}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {
            "manage_employees": {"description": "Manage employee records", "required_params": ["employee_id"]},
            "process_payroll": {"description": "Process payroll", "required_params": ["month", "year"]},
            "track_attendance": {"description": "Track attendance", "required_params": ["employee_id", "date"]},
            "manage_benefits": {"description": "Manage benefits", "required_params": ["employee_id", "benefit_type"]},
            "recruitment": {"description": "Handle recruitment", "required_params": ["position", "description"]},
        }
