from agents.base_agent import BaseAgent

class HeavyMachineryPaAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="omni_heavy_machinery_pa", name="Heavy Machinery Pa", description="Handles pa duties for the heavy_machinery sector.")
        self.sector = "heavy_machinery"
        self.role = "pa"
        self.tier = "SECTOR"
        self.brain = "groq-llama-3"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {"action": "delegate_or_execute", "confidence": 0.95}

    def execute_action(self, action, parameters):
        return {"status": "success", "message": f"Executed by {self.name}"}
