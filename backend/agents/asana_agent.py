"""Asana Agent - Project management and task organization"""
from backend.agents.base_agent import BaseAgent

class AsanaAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Asana Agent"
        self.description = "Project management and task organization"
        self.capabilities = ["create_task", "manage_project", "timeline", "team_collaboration", "reporting"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "task" in intent_lower: return {"action": "create_task", "confidence": 0.9}
        elif "project" in intent_lower: return {"action": "manage_project", "confidence": 0.85}
        elif "timeline" in intent_lower: return {"action": "timeline", "confidence": 0.8}
        return {"action": "create_task", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "create_task": return {"status": "success", "task_id": "TASK_001"}
        elif action == "manage_project": return {"status": "success", "projects": 15}
        elif action == "timeline": return {"status": "success", "on_track": True}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {"create_task": {"description": "Create task", "required_params": ["title"]}, "manage_project": {"description": "Manage project", "required_params": []}, "timeline": {"description": "View timeline", "required_params": []}}
