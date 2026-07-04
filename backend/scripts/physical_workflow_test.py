import time
import os
import sys
import re

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN
from utils.file_system_tools import write_to_desktop

def run_physical_test():
    print("==================================================")
    print(" OMNI-MNC: PHYSICAL WORKFLOW EXECUTION TEST")
    print("==================================================")
    
    # 1. The CEO Command
    ceo_command = "Write the python code for a basic Data Scraping Agent that inherits from BaseAgent. Just return the raw python code."
    print(f"\n[CEO Directive]: {ceo_command}")
    
    # 2. Routing to Tech Sector via Super Brain
    print("\n[Super PA]: Routing directive to Tech Sector Developer Agent...")
    time.sleep(1)
    
    # 3. Super Brain Execution
    print("[Tech Sector]: Generating code via Omni Super Brain...")
    response = GLOBAL_SUPER_BRAIN.ask(ceo_command, context={}, agent_tier="EMPLOYEE")
    raw_code = response["response"]
    brain_used = response["brain_used"]
    print(f"[Tech Sector]: Code successfully generated using {brain_used}.")
    
    # Strip markdown block quotes if present
    clean_code = raw_code
    if "```python" in clean_code:
        clean_code = clean_code.split("```python")[1].split("```")[0].strip()
    elif "```" in clean_code:
        clean_code = clean_code.split("```")[1].split("```")[0].strip()
    
    if not clean_code.startswith("import") and not clean_code.startswith("from"):
        # If the API failed and returned a simulation, just inject a real mock script
        clean_code = """from agents.base_agent import BaseAgent\n\nclass DataScrapingAgent(BaseAgent):\n    def __init__(self):\n        super().__init__(agent_id="scraper", name="Data Scraper", description="Scrapes websites")\n"""
        print("[Tech Sector]: Used fallback simulation code due to API error.")
        
    # 4. Physical Action (File System Write)
    print("\n[Tech Sector]: Initiating physical file system write...")
    file_params = {
        "filename": "data_scraping_agent.py",
        "content": clean_code
    }
    
    result = write_to_desktop(file_params)
    
    if result["status"] == "success":
        print(f"\n[SUCCESS]: {result['message']}")
    else:
        print(f"\n[ERROR]: {result['message']}")

if __name__ == "__main__":
    run_physical_test()
