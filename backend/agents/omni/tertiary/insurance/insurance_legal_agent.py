from agents.base_agent import BaseAgent

class InsuranceLegalAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="omni_insurance_legal", name="Insurance Legal", description="Handles legal duties for the insurance sector.")
        self.sector = "insurance"
        self.role = "legal"
        self.tier = "SECTOR"
        self.brain = "gemini-2.5-flash"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {"action": "delegate_or_execute", "confidence": 0.95}

    def execute_action(self, action, parameters):
        return {"status": "success", "message": f"Executed by {self.name}"}
