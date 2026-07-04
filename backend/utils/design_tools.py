import requests
import os
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

def generate_image(prompt: str, filename: str) -> dict:
    """
    Uses the free Pollinations AI API to generate an image based on a prompt.
    Saves the image to the Omni-MNC-Files desktop folder.
    """
    print(f"[Design Sector]: Designing image for prompt: '{prompt}'...")
    
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Omni-MNC-Files")
            os.makedirs(desktop_folder, exist_ok=True)
            
            filepath = os.path.join(desktop_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            return {"status": "success", "filepath": filepath}
        else:
            return {"status": "error", "message": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def overlay_text_on_image(image_path: str, text: str, output_path: str) -> dict:
    """
    Physically paints a graphic box and text onto an existing image file.
    """
    print("[Design Sector]: Activating Graphic Engine. Overlaying text onto poster...")
    try:
        # Load the original image
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # Create a transparent overlay for the text box
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Define the box dimensions (bottom 40% of the image)
        box_top = int(height * 0.6)
        box_bottom = height
        box_left = 0
        box_right = width
        
        # Draw a semi-transparent black gradient or solid box
        draw.rectangle([box_left, box_top, box_right, box_bottom], fill=(0, 0, 0, 200))
        
        # Merge the overlay with the original image
        final_img = Image.alpha_composite(img, overlay).convert("RGB")
        draw_final = ImageDraw.Draw(final_img)
        
        # Try to load a nice Windows font, fallback to default if missing
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 28)
            title_font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 46)
        except:
            font = ImageFont.load_default()
            title_font = font
            
        # Draw Title
        title_text = "VEL TECH ADMISSIONS OPEN"
        draw_final.text((40, box_top + 20), title_text, font=title_font, fill=(255, 215, 0)) # Gold
        
        # Draw Content text
        y_pos = box_top + 90
        for line in text.split('\n'):
            line = line.strip()
            if line:
                draw_final.text((40, y_pos), line, font=font, fill=(255, 255, 255))
                y_pos += 35
            
        # Save the final Graphic Poster
        final_img.save(output_path, format="JPEG", quality=95)
        return {"status": "success", "filepath": output_path}
        
    except Exception as e:
        print(f"[Design Sector Error]: {str(e)}")
        return {"status": "error", "message": str(e)}
