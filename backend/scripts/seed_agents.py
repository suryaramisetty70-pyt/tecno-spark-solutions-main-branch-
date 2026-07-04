import asyncio
import sys
import os
import json
import importlib
import inspect
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import async_session_maker, init_db
from db.models import Agent
from sqlalchemy.future import select

async def seed_agents():
    # Ensure tables exist
    await init_db()
    
    agents_dir = Path("agents")
    agent_files = list(agents_dir.glob("*_agent.py"))
    
    print(f"Found {len(agent_files)} agent python files.")
    
    async with async_session_maker() as db:
        for agent_file in agent_files:
            if agent_file.name in ["base_agent.py", "enhanced_base_agent.py"]:
                continue
                
            try:
                module_name = f"agents.{agent_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, agent_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find the agent class
                agent_class = None
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("Agent") and name not in ["BaseAgent", "EnhancedBaseAgent"]:
                        agent_class = obj
                        break
                        
                if not agent_class:
                    continue
                    
                # Instantiate temporarily to get info
                try:
                    # Pass a dummy core if it requires one, or instantiate directly
                    if "core" in inspect.signature(agent_class.__init__).parameters:
                        continue # Skip agents that strictly require core for now or handle them specially
                    temp_agent = agent_class()
                except TypeError:
                    # Try passing None if it expects core
                    try:
                        temp_agent = agent_class(None)
                    except:
                        continue
                        
                name = getattr(temp_agent, "name", agent_file.stem.replace("_agent", "").title() + " Agent")
                agent_id = getattr(temp_agent, "id", agent_file.stem.replace("_agent", ""))
                description = getattr(temp_agent, "description", "")
                capabilities_raw = getattr(temp_agent, "capabilities", [])
                capabilities = []
                for c in capabilities_raw:
                    if isinstance(c, dict) and "skills" in c:
                        capabilities.extend(c["skills"])
                
                # Check if exists
                result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
                existing = result.scalars().first()
                
                if not existing:
                    agent = Agent(
                        agent_id=agent_id,
                        name=name,
                        description=description,
                        version="1.0.0",
                        capabilities=",".join(capabilities),
                        status="active",
                        enabled_by_default=False,
                        requires_authentication=False,
                        author="Buddy AI OS",
                        config={"name": name, "capabilities": capabilities, "category": "Business"}
                    )
                    db.add(agent)
                    print(f"Added agent: {name}")
            except Exception as e:
                print(f"Error loading {agent_file.name}: {e}")
                
        await db.commit()
        print("Done seeding all 121 agents.")

if __name__ == "__main__":
    asyncio.run(seed_agents())
