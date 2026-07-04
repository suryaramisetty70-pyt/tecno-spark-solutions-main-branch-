import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN
from utils.research_tools import search_web
from utils.design_tools import generate_image, overlay_text_on_image

def execute_poster_campaign():
    print("==================================================")
    print(" OMNI-MNC: GRAPHIC AD POSTER CAMPAIGN")
    print("==================================================")
    
    # 1. Research Sector
    print("\n[Super PA]: Routing to Research Sector for exact fee data...")
    results = search_web("Vel Tech B.Tech annual tuition fee admission placements", max_results=3)
    research_context = "\n".join([res['snippet'] for res in results])
    
    # 2. Marketing Sector
    print("\n[Super PA]: Routing to Marketing Sector to write Poster Copy...")
    prompt = f"""
    You are a billboard copywriter. Extract the Vel Tech University B.Tech fees and placements from the data below.
    Write exactly 4 short bullet points for an ad poster. Do NOT write anything else. Keep it extremely brief.
    Format example:
    - B.Tech Annual Fee: $X
    - Top Recruiters: Amazon, Google
    - Placements: 90%+ Success
    - Apply Now for 2024!
    
    Data:
    {research_context}
    """
    
    response = GLOBAL_SUPER_BRAIN.ask(prompt, context={}, agent_tier="EXECUTIVE")
    poster_copy = response["response"]
    
    # Clean up markdown asterisks for the graphic
    poster_copy = poster_copy.replace("*", "").replace("`", "").strip()
    
    # 3. Design Sector - Base Image
    print("\n[Super PA]: Routing to Design Sector for Background Plate...")
    desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Omni-MNC-Files")
    base_image_path = os.path.join(desktop_folder, "veltech_bg_plate.jpg")
    
    img_res = generate_image("Wide shot of an ultra-modern university campus building, cinematic, hyperrealistic 8k", "veltech_bg_plate.jpg")
    
    if img_res["status"] == "success":
        # 4. Design Sector - Graphic Overlay
        print("\n[Super PA]: Applying Graphic Engine Overlay...")
        final_poster_path = os.path.join(desktop_folder, "VelTech_Final_Ad_Poster.jpg")
        
        overlay_res = overlay_text_on_image(img_res["filepath"], poster_copy, final_poster_path)
        
        if overlay_res["status"] == "success":
            print(f"\n[SUCCESS]: Physical Ad Poster Graphic completed and saved to {final_poster_path}")
        else:
            print(f"\n[ERROR]: Graphic Engine failed - {overlay_res['message']}")
    else:
        print("\n[ERROR]: Base image generation failed.")

if __name__ == "__main__":
    execute_poster_campaign()
