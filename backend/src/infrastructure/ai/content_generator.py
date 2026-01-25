import google.generativeai as genai
import os
import json
import re
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Prompts directory (in src/prompts - sibling of infrastructure)
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

def load_prompt(category: str, name: str) -> str:
    """Load a prompt from external .txt file"""
    path = PROMPTS_DIR / category / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    print(f"⚠️ Prompt not found: {path}")
    return ""

def load_styles() -> Dict[str, str]:
    """Load style definitions from styles.txt"""
    styles = {}
    content = load_prompt("reels", "styles")
    
    current_style = None
    current_desc = []
    
    for line in content.split("\n"):
        if line.startswith("[") and line.endswith("]"):
            if current_style and current_desc:
                styles[current_style] = " ".join(current_desc).strip()
            current_style = line[1:-1]
            current_desc = []
        elif current_style and line.strip():
            current_desc.append(line.strip())
    
    # Add last style
    if current_style and current_desc:
        styles[current_style] = " ".join(current_desc).strip()
    
    return styles

def clean_json_response(text: str) -> str:
    """Cleans markdown code blocks and fixes common JSON issues."""
    cleaned = text.strip()
    
    # Remove markdown code blocks
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # Fix common JSON issues from AI responses
    cleaned = re.sub(r',\s*(\]|\})', r'\1', cleaned)
    
    return cleaned

def parse_json_safely(text: str) -> Optional[dict]:
    """Try multiple methods to parse JSON from AI response."""
    
    # Method 1: Direct parse after cleaning
    try:
        return json.loads(clean_json_response(text))
    except json.JSONDecodeError:
        pass
    
    # Method 2: Find JSON object with regex
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group()
            json_str = re.sub(r',\s*(\]|\})', r'\1', json_str)
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Method 3: Try to extract scenes array at minimum
    try:
        scenes_match = re.search(r'"scenes"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', text)
        
        if scenes_match:
            scenes_str = '[' + scenes_match.group(1) + ']'
            scenes_str = re.sub(r',\s*(\]|\})', r'\1', scenes_str)
            scenes = json.loads(scenes_str)
            return {
                "title": title_match.group(1) if title_match else "Untitled",
                "scenes": scenes
            }
    except:
        pass
    
    return None

def generate_reels_script(topic: str, style: str = "curious", duration_seconds: int = 60) -> Dict:
    """
    Generates a viral script for a Reel/Short based on a topic.
    Prompts are loaded from external .txt files in prompts/reels/
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={"response_mime_type": "application/json", "temperature": 0.7}
    )

    # Load prompts from external files
    system_role = load_prompt("reels", "system_prompt")
    prompt_template = load_prompt("reels", "script_generation")
    
    # Load styles from file
    style_instructions = load_styles()
    selected_style = style_instructions.get(style, style_instructions.get("curious", ""))
    
    # Build full prompt from template
    prompt = f"{system_role}\n\n{prompt_template}".format(
        topic=topic,
        duration=duration_seconds,
        style_description=selected_style
    )

    try:
        response = model.generate_content(prompt)
        print(f"🎬 Generated Script for '{topic}'")
        
        # Use robust parsing
        script_data = parse_json_safely(response.text)
        
        if script_data and script_data.get('scenes'):
            return script_data
        else:
            print("⚠️ Could not parse JSON, using fallback")
            raise ValueError("Invalid JSON structure")
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        # Fallback structure
        return {
            "title": "Error - Intenta de nuevo",
            "scenes": [
                {
                    "id": 1,
                    "narration": "Lo siento, hubo un problema generando tu historia. Por favor intenta de nuevo con un tema diferente.",
                    "visual_query": "error glitch screen vertical",
                    "duration_estimate": 5
                }
            ]
        }
