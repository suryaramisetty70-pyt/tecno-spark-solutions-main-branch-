from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.super_brain import GLOBAL_SUPER_BRAIN
from db.omni_db import OMNI_DB

app = FastAPI(title="Omni-MNC CEO Command Center")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow Next.js frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    directive: str

@app.get("/")
def health_check():
    return {"status": "Omni-MNC Online", "agents": 1040}

@app.post("/api/command")
def execute_ceo_command(req: CommandRequest):
    # Step 1: Save CEO Directive to DB Memory
    OMNI_DB.save_memory("CEO", req.directive, "Awaiting Processing")
    
    # TRUE SEMANTIC ROUTING (Enterprise Hardening)
    intent_data = GLOBAL_SUPER_BRAIN.get_intent(req.directive)
    intent = intent_data.get("INTENT", "CHAT")
    
    if intent == "CAMPAIGN":
        from core.campaign_manager import GLOBAL_CAMPAIGN_MANAGER
        final_response = GLOBAL_CAMPAIGN_MANAGER.execute_ad_campaign(req.directive)
        brain_used = "Universal Campaign Manager (Semantic Route)"
    else:
        # Standard AI Routing for Chat/General commands
        response = GLOBAL_SUPER_BRAIN.ask(req.directive, context={}, agent_tier="SUPER")
        final_response = response["response"]
        brain_used = response["brain_used"]
    
    # Step 3: Save Agent Action to Memory (Agent Autonomy)
    OMNI_DB.save_memory("SUPER_PA", req.directive, final_response)
    
    return {
        "status": "success",
        "brain_used": brain_used,
        "super_pa_response": final_response,
        "active_sectors": ["Banking", "Tech", "Manufacturing", "Legal"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
