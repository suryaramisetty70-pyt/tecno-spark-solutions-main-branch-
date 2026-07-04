import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agents_dir = os.path.join(backend_dir, "agents")

# Paid agents to delete
to_delete = [
    "twilio_agent.py", "intercom_agent.py", "zendesk_agent.py", "zoom_agent.py",
    "salesforce_agent.py", "hubspot_agent.py", "mailchimp_agent.py", "calendly_agent.py",
    "monday_agent.py", "shopify_agent.py", "aws_agent.py", "azure_agent.py", 
    "gcp_agent.py", "heroku_agent.py"
]

# New free agents to create
to_create = {
    "fonoster_agent.py": {
        "class": "FonosterAgent", "name": "Fonoster Agent", "desc": "Open-source programmable voice and SMS (Twilio alternative)"
    },
    "chatwoot_agent.py": {
        "class": "ChatwootAgent", "name": "Chatwoot Agent", "desc": "Open-source omnichannel customer support (Intercom alternative)"
    },
    "freescout_agent.py": {
        "class": "FreeScoutAgent", "name": "FreeScout Agent", "desc": "Open-source helpdesk and ticketing (Zendesk alternative)"
    },
    "jitsi_agent.py": {
        "class": "JitsiAgent", "name": "Jitsi Agent", "desc": "Open-source encrypted video conferencing (Zoom alternative)"
    },
    "twenty_crm_agent.py": {
        "class": "TwentyCrmAgent", "name": "Twenty CRM Agent", "desc": "Modern open-source CRM (Salesforce/HubSpot alternative)"
    },
    "listmonk_agent.py": {
        "class": "ListmonkAgent", "name": "Listmonk Agent", "desc": "Self-hosted newsletter and mailing list (Mailchimp alternative)"
    },
    "cal_agent.py": {
        "class": "CalAgent", "name": "Cal.com Agent", "desc": "Open-source scheduling and booking (Calendly alternative)"
    },
    "plane_agent.py": {
        "class": "PlaneAgent", "name": "Plane Agent", "desc": "Open-source project management (Monday.com alternative)"
    },
    "medusa_agent.py": {
        "class": "MedusaAgent", "name": "Medusa Agent", "desc": "Open-source headless e-commerce engine (Shopify alternative)"
    },
    "localstack_agent.py": {
        "class": "LocalStackAgent", "name": "LocalStack Agent", "desc": "Local AWS cloud environment for free development"
    },
    "self_host_agent.py": {
        "class": "SelfHostAgent", "name": "Self-Host Agent", "desc": "Docker and Kubernetes orchestrator for free deployments"
    }
}

template = """\"\"\"{name} - {desc}\"\"\"
from agents.base_agent import BaseAgent

class {class_name}(BaseAgent):
    def __init__(self, agent_id="{id}", name="{name}", description="{desc}"):
        super().__init__(agent_id=agent_id, name=name, description=description)
        self.capabilities = ["manage", "integrate", "automate"]
        self.register_tools()

    def process_intent(self, intent, context):
        return {{"action": "manage", "confidence": 0.9}}

    def execute_action(self, action, parameters):
        return {{"status": "success", "message": f"Executed {{action}} on {name}"}}

    def register_tools(self):
        self.tools = []
"""

# Delete old ones
for f in to_delete:
    path = os.path.join(agents_dir, f)
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted {f}")

# Create new ones
for f, data in to_create.items():
    path = os.path.join(agents_dir, f)
    agent_id = f.replace("_agent.py", "")
    content = template.format(
        name=data["name"], desc=data["desc"], class_name=data["class"], id=agent_id
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Created {f}")

print("Migration complete!")
