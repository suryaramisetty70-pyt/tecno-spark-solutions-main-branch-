"""Jira Agent - Project tracking and issue management"""
from agents.base_agent import BaseAgent

class JiraAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="jira_agent", name="Jira Agent", description="Jira project and issue tracking")
        self.name = "Jira Agent"
        self.description = "Jira project and issue tracking"
        self.capabilities = ["create_issues", "manage_sprints", "track_progress", "assign_tasks", "reporting"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "issue" in intent_lower or "create" in intent_lower: return {"action": "create_issues", "confidence": 0.9}
        elif "sprint" in intent_lower: return {"action": "manage_sprints", "confidence": 0.85}
        elif "progress" in intent_lower: return {"action": "track_progress", "confidence": 0.85}
        elif "assign" in intent_lower or "task" in intent_lower: return {"action": "assign_tasks", "confidence": 0.85}
        elif "report" in intent_lower: return {"action": "reporting", "confidence": 0.8}
        return {"action": "create_issues", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "create_issues": return {"status": "success", "issue_id": "JIRA-001"}
        elif action == "manage_sprints": return {"status": "success", "current_sprint": "Sprint 5"}
        elif action == "track_progress": return {"status": "success", "completion": "65%"}
        elif action == "assign_tasks": return {"status": "success", "assigned": 10}
        elif action == "reporting": return {"status": "success", "report_url": "/reports/sprint.pdf"}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {
            "create_issues": {"description": "Create issue", "required_params": ["title", "description"]},
            "manage_sprints": {"description": "Manage sprints", "required_params": ["sprint_id"]},
            "track_progress": {"description": "Track progress", "required_params": ["project_id"]},
            "assign_tasks": {"description": "Assign tasks", "required_params": ["task_id", "assignee"]},
            "reporting": {"description": "Generate reports", "required_params": ["report_type"]},
        }
