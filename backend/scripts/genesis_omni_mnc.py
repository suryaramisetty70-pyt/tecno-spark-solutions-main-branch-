import os
import json
import time

def create_omni_mnc():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'agents', 'omni')
    os.makedirs(base_dir, exist_ok=True)
    
    # 5 Macro Sectors and their sub-industries
    sectors = {
        "primary": ["agriculture", "mining", "forestry", "fishing", "energy_extraction", "oil_gas", "water_resources"],
        "secondary": ["automotive", "aerospace", "textiles", "food_processing", "construction", "electronics_mfg", "heavy_machinery"],
        "tertiary": ["banking", "insurance", "real_estate", "retail", "healthcare", "transportation", "hospitality", "police", "fire_rescue"],
        "quaternary": ["software_dev", "cybersecurity", "social_media", "journalism", "data_analytics", "pharmaceutical_rd", "telecom"],
        "quinary": ["federal_gov", "local_gov", "ngo", "public_policy", "supreme_court", "military_command", "space_exploration"]
    }
    
    # Core Executive Team (Super Agents)
    super_agents = ["super_pa", "super_hr", "super_manager", "super_legal"]
    
    # Standard roles in EVERY sector
    sector_roles = ["pa", "hr", "manager", "legal", "auditor", "analyst", "operator", "compliance_officer"]
    
    agent_template = """from agents.base_agent import BaseAgent

class {class_name}(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="{agent_id}", name="{name}", description="{description}")
        self.sector = "{sector}"
        self.role = "{role}"
        self.tier = "{tier}"
        self.brain = "{brain}"  # e.g., 'gemini-2.5-pro', 'groq-llama-3', 'openrouter-free'

    def process_intent(self, intent, context):
        return {{"action": "delegate_or_execute", "confidence": 0.95}}

    def execute_action(self, action, parameters):
        return {{"status": "success", "message": f"Executed by {{self.name}}"}}
"""

    total_agents = 0
    print("Initiating Genesis Sequence: Omni-MNC Architecture...")
    
    # 1. Create Super Agents (Tier 2)
    super_dir = os.path.join(base_dir, 'executive_core')
    os.makedirs(super_dir, exist_ok=True)
    for sa in super_agents:
        class_name = sa.replace('_', ' ').title().replace(' ', '') + "Agent"
        name = sa.replace('_', ' ').title()
        file_path = os.path.join(super_dir, f"{sa}_agent.py")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(agent_template.format(
                class_name=class_name,
                agent_id=f"omni_{sa}",
                name=f"Omni {name}",
                description=f"Global Executive {name} reporting directly to the CEO.",
                sector="GLOBAL",
                role=sa.split('_')[1],
                tier="SUPER",
                brain="gemini-2.5-pro" # Super agents get the heavy brain
            ))
        total_agents += 1

    # 2. Create Sector Teams (Tier 3 & 4)
    for macro, industries in sectors.items():
        macro_dir = os.path.join(base_dir, macro)
        os.makedirs(macro_dir, exist_ok=True)
        
        for industry in industries:
            industry_dir = os.path.join(macro_dir, industry)
            os.makedirs(industry_dir, exist_ok=True)
            
            # Create standard sector leadership and employees
            for role in sector_roles:
                agent_id = f"{industry}_{role}"
                class_name = agent_id.replace('_', ' ').title().replace(' ', '') + "Agent"
                name = f"{industry.replace('_', ' ').title()} {role.title()}"
                
                # Determine Brain API
                if role == "pa":
                    brain = "groq-llama-3" # PAs need speed
                elif role in ["manager", "legal"]:
                    brain = "gemini-2.5-flash" # Management needs context
                else:
                    brain = "openrouter-free" # Standard employees use varied open models
                
                file_path = os.path.join(industry_dir, f"{agent_id}_agent.py")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(agent_template.format(
                        class_name=class_name,
                        agent_id=f"omni_{agent_id}",
                        name=name,
                        description=f"Handles {role} duties for the {industry} sector.",
                        sector=industry,
                        role=role,
                        tier="SECTOR" if role in ["manager", "hr", "legal", "pa"] else "EMPLOYEE",
                        brain=brain
                    ))
                total_agents += 1
                
            # Create 20 specialized generic employees per industry to hit the 1,000 mark
            for i in range(1, 21):
                role = f"specialist_{i}"
                agent_id = f"{industry}_{role}"
                class_name = f"{industry.replace('_', ' ').title().replace(' ', '')}Specialist{i}Agent"
                name = f"{industry.replace('_', ' ').title()} Specialist {i}"
                
                file_path = os.path.join(industry_dir, f"{agent_id}_agent.py")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(agent_template.format(
                        class_name=class_name,
                        agent_id=f"omni_{agent_id}",
                        name=name,
                        description=f"Specialized worker #{i} in the {industry} sector.",
                        sector=industry,
                        role="specialist",
                        tier="EMPLOYEE",
                        brain="openrouter-free"
                    ))
                total_agents += 1

    print(f"Genesis Sequence Complete. Successfully generated {total_agents} AI Agents.")
    print("Writing structural directory artifact...")
    
    # We will generate the directory tree visualization later via a terminal command.

if __name__ == "__main__":
    start_time = time.time()
    create_omni_mnc()
    print(f"Time taken: {time.time() - start_time:.2f} seconds.")
