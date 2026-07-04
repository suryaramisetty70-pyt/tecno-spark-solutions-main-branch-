"""
Buddy AI OS - Agent Workflow Demonstration
This script demonstrates how multiple agents communicate to solve a complex business request.
"""
import asyncio
import os
import sys

# Add parent dir to path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.buddy_core import BuddyCore
from agents.personal_assistant import PersonalAssistant

async def run_demo():
    print("="*60)
    print(" BUDDY AI OS - MULTI-AGENT WORKFLOW DEMO ")
    print("="*60)
    
    # 1. Initialize Core
    print("\n[System] Initializing Buddy Core...")
    core = BuddyCore()
    PersonalAssistant(core)
    
    # 2. Simulate User Request
    user_id = "demo_user"
    user_intent = "We just onboarded a new client 'Acme Corp' for a $50k software build. Please log the deal, create a project task list, and prepare an invoice."
    print(f"\n[User Request]: {user_intent}\n")
    
    print("-" * 60)
    print("▶ STEP 1: Personal Assistant receives request and routes it...")
    
    # The core intent router will classify this as BUSINESS/PRODUCTIVITY/FINANCE
    # Instead of actually making live LLM calls (which cost money/tokens), we will simulate the output
    # based on the BuddyCore routing logic.
    
    # Let's bypass the actual LLM call for the demo to ensure it runs instantly without API keys
    print("\n▶ STEP 2: Intent Router activates specialized agents:")
    print("  ✓ Sales Agent assigned to log the $50k deal.")
    print("  ✓ Productivity Agent assigned to create project tasks.")
    print("  ✓ Accountant Agent assigned to generate invoice.")
    
    print("\n▶ STEP 3: Execution Output")
    print("  [Sales Agent]: Successfully registered 'Acme Corp' in CRM. Deal value: $50,000. Pipeline stage set to 'Closed Won'.")
    print("  [Productivity Agent]: Created 'Acme Corp Onboarding' project board. Added tasks: 1. Setup Repo 2. Kickoff call 3. Architecture design.")
    print("  [Accountant Agent]: Drafted Invoice #1042 for $50,000 to Acme Corp. Status: Awaiting Approval.")
    
    print("\n▶ STEP 4: Memory Engine")
    print("  [Memory Engine]: Saved context 'Acme Corp onboarding' to long-term memory for future retrieval.")
    
    print("-" * 60)
    print("\n[System] Workflow Complete! This demonstrates how Buddy AI OS turns a single command into a coordinated multi-agent process.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_demo())
