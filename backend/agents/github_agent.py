"""GitHub Agent - Repository and collaboration management"""
from backend.agents.base_agent import BaseAgent

class GitHubAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "GitHub Agent"
        self.description = "GitHub repository and issue management"
        self.capabilities = ["manage_repos", "handle_issues", "pull_requests", "collaborators", "releases"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "repo" in intent_lower: return {"action": "manage_repos", "confidence": 0.9}
        elif "issue" in intent_lower or "bug" in intent_lower: return {"action": "handle_issues", "confidence": 0.85}
        elif "pull" in intent_lower or "pr" in intent_lower: return {"action": "pull_requests", "confidence": 0.85}
        elif "collaborator" in intent_lower: return {"action": "collaborators", "confidence": 0.8}
        elif "release" in intent_lower: return {"action": "releases", "confidence": 0.85}
        return {"action": "manage_repos", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "manage_repos": return {"status": "success", "repos": 25}
        elif action == "handle_issues": return {"status": "success", "open_issues": 12}
        elif action == "pull_requests": return {"status": "success", "open_prs": 5}
        elif action == "collaborators": return {"status": "success", "collaborators": 15}
        elif action == "releases": return {"status": "success", "latest_release": "v1.5.0"}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {
            "manage_repos": {"description": "Manage repositories", "required_params": ["repo_name"]},
            "handle_issues": {"description": "Manage issues", "required_params": ["issue_id"]},
            "pull_requests": {"description": "Manage PRs", "required_params": ["pr_id"]},
            "collaborators": {"description": "Manage collaborators", "required_params": ["user_id"]},
            "releases": {"description": "Manage releases", "required_params": ["repo_id"]},
        }
