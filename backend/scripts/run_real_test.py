import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.buddy_core import BuddyCore
from agents.personal_assistant import PersonalAssistant

async def main():
    print("Initializing your company's BuddyCore AI System...")
    core = BuddyCore()
    PersonalAssistant(core)
    
    print("\nSending your exact request into the company system:")
    intent = "find the trading prices which belongs today and make a report to me"
    print(f"Request: '{intent}'")
    
    print("\nBuddyCore is processing... (This is actually hitting your LLM APIs)")
    
    try:
        # Route through the actual intent router of the company
        result = await core.route_intent(
            user_id="test_user",
            intent=intent,
            context={}
        )
        
        print("\n" + "="*50)
        print("COMPANY SYSTEM RESPONSE:")
        print("="*50)
        print(f"Agent ID that handled this: {result.agent_id}")
        print("\nResponse Output:\n")
        print(result.response)
        print("="*50)
        
    except Exception as e:
        print(f"\nError from your company system: {e}")

if __name__ == "__main__":
    asyncio.run(main())
