import time
import os
import sys

# Ensure the backend directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN
from db.omni_db import OMNI_DB

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def run_training_simulation():
    print_header("OMNI-MNC: AUTONOMOUS TRAINING SIMULATION")
    print("[CEO (Antigravity)]: Initiating training protocols across 3 key sectors.")
    
    training_tasks = [
        {
            "sector": "Tech & Software",
            "tier": "EMPLOYEE",
            "task": "Write a 3-sentence summary on how to optimize a Python FastAPI server for high concurrency, referencing Netflix's architecture."
        },
        {
            "sector": "Banking & Finance",
            "tier": "EMPLOYEE",
            "task": "Explain the concept of 'liquidity risk' in one paragraph, acting like a JP Morgan senior analyst."
        },
        {
            "sector": "Legal",
            "tier": "SECTOR",
            "task": "Draft a very brief, 2-sentence Non-Disclosure Agreement (NDA) clause protecting trade secrets."
        }
    ]

    report = "# 📊 Omni-MNC Autonomous Training Report\n\n"
    report += "**Conducted by:** Interim CEO (Antigravity)\n"
    report += "**Objective:** Verify real-world API connectivity and sector-specific tone.\n\n"

    for idx, task_data in enumerate(training_tasks, 1):
        sector = task_data["sector"]
        tier = task_data["tier"]
        task = task_data["task"]
        
        print(f"\n[{sector} Sector] Training Initiated...")
        print(f"Task: {task}")
        
        # Log to DB
        OMNI_DB.save_memory(f"Trainer_CEO", task, "Pending Execution")
        
        # Execute via Super Brain
        start_time = time.time()
        response = GLOBAL_SUPER_BRAIN.ask(task, context={}, agent_tier=tier)
        duration = time.time() - start_time
        
        brain_used = response["brain_used"]
        actual_response = response["response"]
        
        # Log result to DB
        OMNI_DB.save_memory(f"{sector}_Agent", task, actual_response)
        
        print(f"Brain Used: {brain_used}")
        print(f"Response Time: {duration:.2f} seconds")
        print(f"Result: {actual_response[:100]}...") # Print snippet to terminal
        
        # Build Report
        report += f"## Test {idx}: {sector} Sector\n"
        report += f"- **Task:** {task}\n"
        report += f"- **Brain Used:** {brain_used} ({duration:.2f}s response time)\n"
        report += f"- **Output:** \n> {actual_response.replace(chr(10), chr(10)+'> ')}\n\n"
        report += "---\n\n"
        
        time.sleep(1) # Prevent rate limits

    print("\n[SYSTEM] Training complete. Generating report artifact...")
    
    # Save the report artifact
    artifact_path = r"C:\Users\surya\.gemini\antigravity\brain\5e38a612-32a4-4bac-a69a-28e5d618e239\training_report.md"
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Report saved to {artifact_path}")

if __name__ == "__main__":
    run_training_simulation()
