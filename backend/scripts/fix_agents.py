import glob
import re

files = glob.glob("agents/*_agent.py")
fixed = 0
for f in files:
    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()
    
    if "super().__init__()" in content and "from agents.base_agent import BaseAgent" in content:
        name_match = re.search(r'self\.name\s*=\s*"([^"]+)"', content)
        desc_match = re.search(r'self\.description\s*=\s*"([^"]+)"', content)
        
        if name_match:
            agent_name = name_match.group(1)
            agent_id = agent_name.lower().replace(" ", "_")
            description = desc_match.group(1) if desc_match else agent_name
            
            content = content.replace(
                "super().__init__()",
                f'super().__init__(agent_id="{agent_id}", name="{agent_name}", description="{description}")'
            )
            
            # Also need to remove abstract method errors - make process_intent non-abstract
            # These simple agents don't use async, so we need to wrap them
            
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(content)
            fixed += 1
            print(f"Fixed: {f} -> {agent_name}")

print(f"\nTotal fixed: {fixed}")
