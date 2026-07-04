import time
import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN
from utils.file_system_tools import write_to_desktop
from utils.research_tools import search_web
from utils.design_tools import generate_image

def execute_veltech_campaign():
    print("==================================================")
    print(" OMNI-MNC: AUTONOMOUS MULTI-SECTOR CAMPAIGN")
    print("==================================================")
    
    # 1. The Directive
    print("\n[Super PA]: Directive received: Launch Vel Tech Admissions Campaign.")
    time.sleep(1)
    
    # 2. Research Sector Execution
    print("\n[Super PA]: Routing to Research Sector...")
    research_data = search_web("Vel Tech University admissions open courses rankings", max_results=3)
    
    context_string = ""
    for idx, res in enumerate(research_data):
        context_string += f"Source {idx+1}: {res['title']} - {res['snippet']}\n"
    
    print("[Research Sector]: Live internet scan complete. Data acquired.")
    
    # 3. Marketing Sector Execution
    print("\n[Super PA]: Routing live data to Marketing Sector...")
    prompt = f"""
    Act as an elite marketing director. Use the following live research data to write an exciting, 
    highly persuasive 'Admissions Open' pamphlet for Vel Tech University. 
    Use catchy headings and bullet points. Make it sound prestigious.
    
    Research Data:
    {context_string}
    """
    
    response = GLOBAL_SUPER_BRAIN.ask(prompt, context={}, agent_tier="EXECUTIVE")
    pamphlet_text = response["response"]
    print(f"[Marketing Sector]: Pamphlet written successfully using {response['brain_used']}.")
    
    # 4. Design Sector Execution
    print("\n[Super PA]: Routing to Design Sector...")
    image_prompt = "A beautiful, futuristic, and prestigious university campus at sunrise, students walking, ultra realistic, highly detailed, cinematic lighting"
    image_result = generate_image(image_prompt, "veltech_promotional_image.jpg")
    
    if image_result["status"] == "success":
        print(f"[Design Sector]: Promotional image generated and saved to {image_result['filepath']}")
        
        # Embed the image in the pamphlet
        final_pamphlet = f"# Vel Tech University\n\n![Vel Tech Campus](./veltech_promotional_image.jpg)\n\n{pamphlet_text}"
    else:
        print(f"[Design Sector]: Image generation failed - {image_result['message']}")
        final_pamphlet = pamphlet_text
        
    # 5. Physical Deployment
    print("\n[Super PA]: Deploying final campaign assets to CEO's Desktop...")
    file_params = {
        "filename": "veltech_admissions_pamphlet.md",
        "content": final_pamphlet
    }
    
    write_result = write_to_desktop(file_params)
    
    if write_result["status"] == "success":
        print("\n[SUCCESS]: Operation Vel Tech Campaign completed. Assets saved to Omni-MNC-Files.")
    else:
        print(f"\n[ERROR]: Failed to save pamphlet - {write_result['message']}")

if __name__ == "__main__":
    execute_veltech_campaign()
