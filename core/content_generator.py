import google.generativeai as genai
import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Configure API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def clean_json_response(text: str) -> str:
    """Cleans markdown code blocks to ensure valid JSON."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def generate_reels_script(topic: str, style: str = "curious", duration_seconds: int = 60) -> Dict:
    """
    Generates a viral script for a Reel/Short based on a topic.
    Returns structured JSON with scenes, narration, and visual queries.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp", # Using fast model for responsiveness
        generation_config={"response_mime_type": "application/json", "temperature": 0.8}
    )

    system_role = """Eres un experto guionista de TikTok y Reels con millones de seguidores. 
Tu especialidad es crear contenido VIRAL que retiene la atención desde el primer segundo.
Entiendes perfectamente el ritmo, los ganchos (hooks) y la estructura narrativa de 60 segundos."""

    # Style definitions
    style_instructions = {
        "curious": "Estilo 'Sabías que', datos curiosos, tono fascinante y educativo pero rápido.",
        "horror": "Estilo Creepypasta/Terror, tono de suspenso, final con giro inesperado.",
        "motivational": "Estilo estoico/gym, voz profunda, frases contundentes, filosofía de vida.",
        "funny": "Estilo stand-up, observaciones sarcásticas, situaciones relatables."
    }
    
    selected_style = style_instructions.get(style, style_instructions["curious"])

    prompt = f"""
{system_role}

<task>
Crea un guion TOTALMENTE COMPLETO para un Reel/Short sobre el tema: "{topic}".
El video debe durar máximo {duration_seconds} segundos.
Estilo: {selected_style}
</task>

<structure_rules>
1. **HOOK (0-3s)**: La primera frase debe ser imposible de ignorar. (e.g. "Deja de hacer esto si quieres vivir").
2. **BODY**: Desarrollo rápido. Frases cortas. Sin relleno.
3. **CTA (Final)**: Llamado a la acción natural (e.g. "Sígueme para parte 2").
4. **VISUALES**: Para cada frase, describe EXACTAMENTE qué buscar en un banco de imágenes (Pexels/Unsplash).
   - Usa términos en INGLÉS para la búsqueda visual (visual_query).
   - Especifica "vertical", "4k", "cinematic".
</structure_rules>

<output_schema>
Devuelve ÚNICAMENTE este JSON exacto:
{{
  "title": "Título Clickbait del video",
  "estimated_duration": 55,
  "scenes": [
    {{
      "id": 1,
      "narration": "Texto exacto que dirá la voz en off",
      "visual_query": "Descripción visual detallada en INGLÉS para buscar en stock footage (e.g. 'dark forest cinematic vertical 4k')",
      "duration_estimate": 3.5
    }}
  ]
}}
</output_schema>

<critical>
- El total de 'duration_estimate' DEBE sumar entre 50s y 60s.
- El 'visual_query' debe ser optimizado para buscadores de stock (palabras clave, no frases complejas).
- Siempre incluye 'vertical' en las queries visuales.
- **IMPORTANTE**: Detecta el idioma del 'topic'. Si el tema está en ESPAÑOL, el guion (narration) y título DEBEN estar en ESPAÑOL. Si está en Inglés, en Inglés.
</critical>
"""

    try:
        response = model.generate_content(prompt)
        print(f"🎬 Generated Script for '{topic}'")
        
        script_data = json.loads(clean_json_response(response.text))
        
        # Validation/Fallback logic could go here
        
        return script_data
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        # Fallback structure
        return {
            "title": "Error generating script",
            "scenes": [
                {
                    "id": 1,
                    "narration": "Lo siento, tuve un problema generando tu historia. Intenta de nuevo.",
                    "visual_query": "glitch screen error vertical",
                    "duration_estimate": 5
                }
            ]
        }
