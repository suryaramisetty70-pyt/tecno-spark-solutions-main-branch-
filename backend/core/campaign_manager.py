import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.super_brain import GLOBAL_SUPER_BRAIN
from utils.research_tools import search_web
from utils.design_tools import generate_image, overlay_text_on_image

class CampaignManager:
    @staticmethod
    def execute_ad_campaign(directive: str) -> str:
        """
        Executes a full multi-sector ad campaign based on a user directive.
        Returns a status string to be spoken back to the user via the API.
        """
        print(f"\n--- CAMPAIGN MANAGER TRIGGERED ---")
        
        # 1. Entity Extraction
        target_prompt = f"Extract only the main entity (company, product, or school name) from this directive. Only return the name. Directive: '{directive}'"
        res = GLOBAL_SUPER_BRAIN.ask(target_prompt, context={}, agent_tier="CEO")
        target_entity = res["response"].replace("`", "").strip()
        
        # 2. Research Sector
        print(f"[CampaignManager]: Researching {target_entity}...")
        search_results = search_web(f"{target_entity} key features details pricing", max_results=2)
        research_context = "\n".join([r['snippet'] for r in search_results])
        
        # 3. Marketing Sector
        print(f"[CampaignManager]: Drafting ad copy for {target_entity}...")
        marketing_prompt = f"""
        You are an elite copywriter. Based on the data below, write exactly 4 short bullet points for a graphic ad poster about {target_entity}.
        Do NOT write anything else.
        Data: {research_context}
        """
        copy_res = GLOBAL_SUPER_BRAIN.ask(marketing_prompt, context={}, agent_tier="EXECUTIVE")
        poster_copy = copy_res["response"].replace("*", "").replace("`", "").strip()
        
        # 4. Design Sector
        print(f"[CampaignManager]: Generating background plate for {target_entity}...")
        desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Omni-MNC-Files")
        os.makedirs(desktop_folder, exist_ok=True)
        
        safe_name = "".join([c for c in target_entity if c.isalnum() or c == " "]).replace(" ", "_")
        bg_filename = f"{safe_name}_bg.jpg"
        final_filename = f"{safe_name}_Final_Ad_Poster.jpg"
        
        img_prompt = f"A highly professional, stunning, and cinematic background representing {target_entity}, hyperrealistic 8k"
        img_res = generate_image(img_prompt, bg_filename)
        
        if img_res["status"] == "success":
            print(f"[CampaignManager]: Applying text overlay...")
            final_poster_path = os.path.join(desktop_folder, final_filename)
            overlay_res = overlay_text_on_image(img_res["filepath"], poster_copy, final_poster_path)
            
            if overlay_res["status"] == "success":
                return f"Campaign Operation successful. I have researched {target_entity}, designed the graphic, and saved the final Ad Poster to your Desktop."
            else:
                return f"I researched {target_entity}, but the Graphic Engine failed to apply the text overlay."
        else:
            return f"Operation failed. The Design Sector could not generate the background image for {target_entity}."

GLOBAL_CAMPAIGN_MANAGER = CampaignManager()
