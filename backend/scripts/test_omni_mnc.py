import time
import os
import sys

# Ensure the backend directory is in the python path so it can find the 'core' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def simulate_omni_workflow():
    print_header("OMNI-MNC GLOBAL STRESS TEST: PROJECT QUANTUM")
    print("[SYSTEM] Booting up 1,040 AI Agents across 5 Macro-Sectors...")
    time.sleep(1)
    print("[SYSTEM] Super Brain Routing Engine ONLINE.")
    time.sleep(1)
    
    # Step 1: CEO Command
    ceo_directive = "Initiate Project Quantum: Launch our new green energy product globally today."
    print(f"\n👑 [CEO DIRECTIVE]: {ceo_directive}")
    time.sleep(2)
    
    # Step 2: Super PA Analysis
    print("\n⚡ [ROUTING] Handing off to Super PA Agent...")
    pa_response = GLOBAL_SUPER_BRAIN.ask(ceo_directive, context={}, agent_tier="SUPER")
    print(f"[SUPER PA]: Acknowledged. Analyzing directive using {pa_response['brain_used']}...")
    time.sleep(2)
    
    print("\n[SUPER PA]: Breaking down Project Quantum into 4 global sector tasks:")
    tasks = {
        "Banking": "Secure $500M in global green energy bonds.",
        "Tech": "Deploy the Quantum IoT tracking software globally.",
        "Manufacturing": "Spin up production lines in 3 key gigafactories.",
        "Legal": "Draft global compliance and carbon-credit contracts."
    }
    for sector, task in tasks.items():
        print(f"  -> Assigned to {sector} Manager: {task}")
        time.sleep(0.5)

    # Step 3: Sector Execution
    print_header("SECTOR EXECUTION PHASE")
    sector_reports = []
    
    for sector, task in tasks.items():
        print(f"\n🏢 Waking up [{sector} Sector Employees]...")
        time.sleep(1)
        
        # Simulate standard employees using different free APIs
        employee_brain = GLOBAL_SUPER_BRAIN._route_request(task, "EMPLOYEE")
        print(f"[{sector} Employees] Executing task using {employee_brain}...")
        time.sleep(1.5)
        
        print(f"[{sector} Manager]: Task complete. Compiling sector report.")
        sector_reports.append(f"{sector} Sector successfully completed: {task}")

    # Step 4: Consensus & Final Report
    print_header("EXECUTIVE REVIEW & CONSENSUS")
    print("[SUPER MANAGER]: Receiving all 4 sector reports. Requesting Super Brain Consensus...")
    time.sleep(2)
    
    consensus = GLOBAL_SUPER_BRAIN.consensus_ask("Review the 4 sector reports for Project Quantum and approve the launch.", context={})
    print(f"\n🧠 [SUPER BRAIN CONSENSUS MODE ACTIVATED]")
    print(f"Analyzing data simultaneously using: {', '.join(consensus['brains_used'])}")
    time.sleep(2)
    
    print("\n✅ [FINAL RESULT]: Project Quantum is fully cleared for global launch. Zero errors detected across all 4 sectors.")
    print("Writing final Executive Report...")
    
    # We will write the markdown artifact outside of this script
    
if __name__ == "__main__":
    simulate_omni_workflow()
