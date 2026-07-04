import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# The secure sandbox directory for Omni-MNC
DESKTOP_DIR = r"C:\Users\surya\Desktop\Omni-MNC-Files"

def _ensure_dir():
    os.makedirs(DESKTOP_DIR, exist_ok=True)

def write_to_desktop(params: Dict[str, Any]) -> Dict[str, Any]:
    """Writes a file to the CEO's desktop Omni-MNC-Files folder."""
    _ensure_dir()
    filename = params.get("filename")
    content = params.get("content")
    
    if not filename or not content:
        return {"status": "error", "message": "Missing filename or content"}
        
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
    filepath = os.path.join(DESKTOP_DIR, safe_filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"Successfully wrote {safe_filename} to Desktop/Omni-MNC-Files"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to write file: {str(e)}"}

def read_from_desktop(params: Dict[str, Any]) -> Dict[str, Any]:
    """Reads a file from the CEO's desktop Omni-MNC-Files folder."""
    _ensure_dir()
    filename = params.get("filename")
    
    if not filename:
        return {"status": "error", "message": "Missing filename"}
        
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
    filepath = os.path.join(DESKTOP_DIR, safe_filename)
    
    if not os.path.exists(filepath):
        return {"status": "error", "message": f"File {safe_filename} does not exist in Desktop/Omni-MNC-Files"}
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": f"Failed to read file: {str(e)}"}
