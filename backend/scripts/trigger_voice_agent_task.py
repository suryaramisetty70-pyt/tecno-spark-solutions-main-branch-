import time
import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN
from utils.file_system_tools import write_to_desktop

def trigger_autonomous_task():
    print("==================================================")
    print(" OMNI-MNC: AUTONOMOUS TASK EXECUTION")
    print("==================================================")
    
    # 1. The CEO Command
    ceo_command = """
    Write a complete Python script for a basic AI Voice Agent. 
    It must use 'SpeechRecognition' for listening (microphone input) and 'pyttsx3' for speaking. 
    It should loop continuously, listen to the user, and use a dummy text response generator to talk back.
    Return ONLY the raw python code, nothing else. No markdown formatting.
    """
    print("\n[CEO Directive]: Build a free AI Voice Agent.")
    
    # 2. Routing
    print("\n[Super PA]: Directive received. Routing to Tech Sector (Developer Agent)...")
    time.sleep(1)
    
    # 3. Autonomous Execution via Super Brain
    print("[Tech Sector]: Designing and writing Voice Agent code autonomously...")
    response = GLOBAL_SUPER_BRAIN.ask(ceo_command, context={}, agent_tier="EMPLOYEE")
    raw_code = response["response"]
    
    # Strip any markdown blocks if the LLM included them
    clean_code = raw_code
    if "```python" in clean_code:
        clean_code = clean_code.split("```python")[1].split("```")[0].strip()
    elif "```" in clean_code:
        clean_code = clean_code.split("```")[1].split("```")[0].strip()
        
    print(f"[Tech Sector]: Code completed. Brain Used: {response['brain_used']}")
    
    # 4. Physical Action
    print("[Tech Sector]: Deploying Voice Agent to the physical Desktop...")
    file_params = {
        "filename": "voice_agent.py",
        "content": clean_code
    }
    
    result = write_to_desktop(file_params)
    
    if result["status"] == "success":
        print(f"\n[SUCCESS]: Tech Sector successfully built and saved voice_agent.py to Omni-MNC-Files")
    else:
        print(f"\n[ERROR]: Failed to save - {result['message']}")

if __name__ == "__main__":
    trigger_autonomous_task()
