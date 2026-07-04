from agents.base_agent import BaseAgent

class OilGasLegalAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="omni_oil_gas_legal", name="Oil Gas Legal", description="Handles legal duties for the oil_gas sector.")
        self.sector = "oil_gas"
        self.role = "legal"
        self.tier = "SECTOR"
        self.brain = "gemini-2.5-flash"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {"action": "delegate_or_execute", "confidence": 0.95}

    def execute_action(self, action, parameters):
        return {"status": "success", "message": f"Executed by {self.name}"}
