from agents.base_agent import BaseAgent

class BankingOperatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="omni_banking_operator", name="Banking Operator", description="Handles operator duties for the banking sector.")
        self.sector = "banking"
        self.role = "operator"
        self.tier = "EMPLOYEE"
        self.brain = "openrouter-free"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {"action": "delegate_or_execute", "confidence": 0.95}

    def execute_action(self, action, parameters):
        return {"status": "success", "message": f"Executed by {self.name}"}
