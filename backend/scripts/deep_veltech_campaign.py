import time
import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN
from utils.file_system_tools import write_to_desktop
from utils.research_tools import search_web

def execute_deep_campaign():
    print("==================================================")
    print(" OMNI-MNC: DEEP-DIVE RESEARCH CAMPAIGN")
    print("==================================================")
    
    print("\n[Super PA]: Directive received: Deep Research Vel Tech University Promotion Page.")
    
    # 1. Research Sector - Deep Scans
    print("\n[Super PA]: Routing to Research Sector for Deep Scans...")
    
    scan_queries = [
        "Vel Tech University official fee structure B.Tech engineering 2023 2024",
        "Vel Tech University highest package average placement recruiters",
        "Vel Tech University campus facilities ranking NIRF"
    ]
    
    aggregated_context = ""
    
    for i, query in enumerate(scan_queries):
        print(f"[Research Sector]: Executing Scan {i+1}/3: '{query}'...")
        results = search_web(query, max_results=3)
        for res in results:
            aggregated_context += f"- {res['title']}: {res['snippet']}\n"
        time.sleep(1) # Prevent rate limiting
        
    print("[Research Sector]: Deep internet scans complete. Massive dataset acquired.")
    
    # 2. Marketing Sector
    print("\n[Super PA]: Routing dataset to Marketing Sector...")
    prompt = f"""
    Act as an elite university marketing director. Write a highly professional, extremely detailed 
    College Promotion Page for Vel Tech University. 
    
    CRITICAL: You MUST include a detailed 'Fee Structure' section and a 'Placement Records' section 
    using the exact numbers from the research data provided below. Make the content highly engaging 
    for prospective students. Use professional markdown formatting.
    
    Research Data:
    {aggregated_context}
    """
    
    response = GLOBAL_SUPER_BRAIN.ask(prompt, context={}, agent_tier="EXECUTIVE")
    promotion_page = response["response"]
    print(f"[Marketing Sector]: Professional Promotion Page written using {response['brain_used']}.")
    
    # Clean markdown blocks
    if "```markdown" in promotion_page:
        promotion_page = promotion_page.split("```markdown")[1].split("```")[0].strip()
        
    final_content = f"![Vel Tech Campus](./veltech_promotional_image.jpg)\n\n" + promotion_page
    
    # 3. Physical Deployment
    print("\n[Super PA]: Deploying final deep-dive page to CEO's Desktop...")
    file_params = {
        "filename": "veltech_professional_promotion.md",
        "content": final_content
    }
    
    write_result = write_to_desktop(file_params)
    
    if write_result["status"] == "success":
        print("\n[SUCCESS]: Operation Deep-Dive completed. Assets saved to Omni-MNC-Files.")
    else:
        print(f"\n[ERROR]: Failed to save page - {write_result['message']}")

if __name__ == "__main__":
    execute_deep_campaign()
