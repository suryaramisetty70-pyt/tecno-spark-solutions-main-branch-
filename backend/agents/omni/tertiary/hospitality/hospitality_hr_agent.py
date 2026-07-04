from agents.base_agent import BaseAgent

class HospitalityHrAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="omni_hospitality_hr", name="Hospitality Hr", description="Handles hr duties for the hospitality sector.")
        self.sector = "hospitality"
        self.role = "hr"
        self.tier = "SECTOR"
        self.brain = "openrouter-free"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {"action": "delegate_or_execute", "confidence": 0.95}

    def execute_action(self, action, parameters):
        return {"status": "success", "message": f"Executed by {self.name}"}
