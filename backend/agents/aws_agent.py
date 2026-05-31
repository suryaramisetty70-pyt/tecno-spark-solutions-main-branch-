"""AWS Agent - Cloud infrastructure management"""
from backend.agents.base_agent import BaseAgent

class AwsAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "AWS Agent"
        self.description = "AWS cloud infrastructure management"
        self.capabilities = ["manage_ec2", "manage_s3", "database", "lambda", "monitoring"]
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "instance" in intent_lower or "ec2" in intent_lower: return {"action": "manage_ec2", "confidence": 0.9}
        elif "storage" in intent_lower or "s3" in intent_lower: return {"action": "manage_s3", "confidence": 0.85}
        elif "database" in intent_lower or "rds" in intent_lower: return {"action": "database", "confidence": 0.85}
        elif "lambda" in intent_lower: return {"action": "lambda", "confidence": 0.85}
        elif "monitor" in intent_lower: return {"action": "monitoring", "confidence": 0.8}
        return {"action": "manage_ec2", "confidence": 0.7}

    def execute_action(self, action, parameters):
        if action == "manage_ec2": return {"status": "success", "instances": 50}
        elif action == "manage_s3": return {"status": "success", "buckets": 20}
        elif action == "database": return {"status": "success", "databases": 15}
        elif action == "lambda": return {"status": "success", "functions": 100}
        elif action == "monitoring": return {"status": "success", "health": "all green"}
        return {"status": "error"}

    def register_tools(self):
        self.tools = {"manage_ec2": {"description": "Manage EC2", "required_params": []}, "manage_s3": {"description": "Manage S3", "required_params": []}, "database": {"description": "Manage RDS", "required_params": []}, "lambda": {"description": "Manage Lambda", "required_params": []}, "monitoring": {"description": "Get monitoring", "required_params": []}}
