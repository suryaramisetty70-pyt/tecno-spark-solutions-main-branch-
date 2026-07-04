from agents.base_agent import BaseAgent

class HeavyMachinerySpecialist14Agent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="omni_heavy_machinery_specialist_14", name="Heavy Machinery Specialist 14", description="Specialized worker #14 in the heavy_machinery sector.")
        self.sector = "heavy_machinery"
        self.role = "specialist"
        self.tier = "EMPLOYEE"
        self.brain = "openrouter-free"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {"action": "delegate_or_execute", "confidence": 0.95}

    def execute_action(self, action, parameters):
        return {"status": "success", "message": f"Executed by {self.name}"}
