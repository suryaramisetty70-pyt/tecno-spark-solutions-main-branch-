from typing import Dict, Any
from core.buddy_core import BuddyCore

class PersonalAssistant:
    """The main front-facing agent for Buddy AI OS"""
    
    def __init__(self, core: BuddyCore):
        self.core = core
        self.name = "Personal Assistant"
        self.id = "personal_assistant"
        
        # Register with core
        self.core.register_agent(self.id, self)
        
    async def __call__(self, intent: str, context: Dict[str, Any]) -> str:
        """Process a message and return an AI response"""
        
        # Build memory context if available
        memory_text = ""
        if "conversation_history" in context:
            history = "\n".join(context["conversation_history"])
            memory_text += f"Recent conversation history:\n{history}\n\n"
            
        system_prompt = f"""You are Buddy, the Personal Assistant AI for the Buddy AI Operating System (developed by Tecno Spark Solutions).
You are extremely smart, fast, and helpful. You act as the central brain of this operating system.
Your goal is to assist the user with any task they need.

{memory_text}
Respond directly to the user's latest request below. Keep it concise, helpful, and friendly."""

        response = await self.core.ai_provider.generate_response(
            system_prompt=system_prompt,
            user_prompt=intent
        )
        
        return response
