from agents.base_agent import BaseAgent

class HeavyMachineryOperatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="omni_heavy_machinery_operator", name="Heavy Machinery Operator", description="Handles operator duties for the heavy_machinery sector.")
        self.sector = "heavy_machinery"
        self.role = "operator"
        self.tier = "EMPLOYEE"
        self.brain = "openrouter-free"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {"action": "delegate_or_execute", "confidence": 0.95}

    def execute_action(self, action, parameters):
        return {"status": "success", "message": f"Executed by {self.name}"}
