import os
import time
import google.generativeai as genai
from core.schema import VideoAnalysis
from core.calibration import get_wps_for_voice

# Configure API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def upload_to_gemini(path: str, mime_type: str = "video/mp4"):
    """
    Uploads the given file to Gemini.
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """
    Waits for the uploaded files to be processed and active.
    """
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")

def clean_json_response(text: str) -> str:
    """
    Cleans Gemini response to ensure valid JSON.
    Removes markdown code blocks (```json ... ```).
    """
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def analyze_video_content(video_path: str, style: str = "viral", pace: str = "fast") -> VideoAnalysis:
    """
    Single-stage unified pipeline:
    - Gemini analyzes video and generates narrative simultaneously
    - Returns complete beats with timestamps and scripts in one call
    """
    # 1. Upload
    video_file = upload_to_gemini(video_path)
    wait_for_files_active([video_file])

    # --- UNIFIED ANALYSIS & NARRATION ---
    print("   ↳ 🎬 Analyzing video and generating narrative...")
    
    from core.prompts import get_system_instruction
    
    # Get base system instruction with style and pace
    base_instruction = get_system_instruction(style, pace)
    
    # Get video duration from file
    from core.video import check_video_duration
    video_duration = check_video_duration(video_path)
    print(f"   📹 Video duration: {video_duration:.1f}s")
    
    # Calculate WPS for narrative
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    words_per_sec = get_wps_for_voice(voice_id, language="es", style=style)
    total_words_max = int(video_duration * words_per_sec * 0.85)
    print(f"   📊 Using calibrated WPS: {words_per_sec:.2f} words/second")
    print(f"   📝 Target narrative length: ~{total_words_max} words")
    
    unified_system_prompt = f"""{base_instruction}

<segmented_continuous_narrative_approach>
ENFOQUE DE NARRATIVA CONTINUA SEGMENTADA:

Este sistema genera UNA NARRATIVA COMPLETA coherente que luego se DIVIDE en segmentos sincronizados con cada beat visual.

PROCESO:
1. Analiza el video completo y comprende la historia
2. Crea beats visuales con timestamps precisos
3. Escribe UNA narrativa completa fluida (~{total_words_max} palabras totales)
4. DIVIDE esa narrativa en segmentos, asignando cada parte al beat correspondiente

CLAVE: La narrativa debe ser UNA HISTORIA COHERENTE que se cuenta de forma continua,
pero dividida inteligentemente para que cada beat tenga su porción sincronizada.
</segmented_continuous_narrative_approach>

<beat_creation>
CREACIÓN DE BEATS VISUALES:
- Analiza el video y crea beats con timestamps precisos
- Cada beat representa un momento visual clave
- Incluye: id, start_s, end_s, visual_summary
- Calcula duración de cada beat para distribuir palabras
</beat_creation>

<narrative_segmentation>
SEGMENTACIÓN DE LA NARRATIVA - MUY IMPORTANTE:

El video dura {video_duration:.1f}s.
La voz TTS tiene velocidad de {words_per_sec:.1f} palabras/segundo.
Palabras totales disponibles: ~{total_words_max}

PASO 1: ESCRIBIR NARRATIVA COMPLETA
Escribe primero la historia completa en overall.full_narrative_script:
- Inicio enganchante
- Desarrollo coherente
- Cierre satisfactorio
- Tercera persona siempre
- Nombres de personajes consistentes
- Total: ~{total_words_max} palabras

PASO 2: DIVIDIR EN SEGMENTOS POR BEAT
Para cada beat, asigna un SEGMENTO de la narrativa completa:
- El segmento debe corresponder temporalmente a lo que se ve en ese beat
- Calcula palabras por beat usando: (end_s - start_s) × {words_per_sec:.1f} × 0.85
- Los segmentos deben fluir naturalmente uno tras otro
- Juntos, los segmentos forman la narrativa completa

EJEMPLO (video 20s, 3 beats):

overall.full_narrative_script: "En las sombras de la noche, El Jakal prepara su jugada más arriesgada. Cada movimiento es preciso, calculado. Sabe que no hay margen de error. Las calles están vacías, pero la tensión es palpable. Marcus observa desde la distancia. Este es el momento que definirá todo."

beat[0] (0-7s, ~14 palabras): 
  visual: "Hombre camina por calles oscuras"
  script: "En las sombras de la noche, El Jakal prepara su jugada más arriesgada."

beat[1] (7-13s, ~12 palabras):
  visual: "Close-up de manos ajustando equipo"
  script: "Cada movimiento es preciso, calculado. Sabe que no hay margen de error."

beat[2] (13-20s, ~14 palabras):
  visual: "Otra persona observando desde lejos"
  script: "Las calles están vacías, pero la tensión es palpable. Marcus observa desde la distancia."

REGLAS CRÍTICAS:
- Cada beat.voiceover.script debe tener EXACTAMENTE las palabras calculadas (±2 aceptable)
- Los scripts deben ser PARTES CONSECUTIVAS de la narrativa completa
- NO repitas información entre beats
- La suma de todos los scripts = narrativa completa
- Mantén coherencia narrativa absoluta
</narrative_segmentation>

<character_naming_rules>
CONTINUIDAD DE PERSONAJES:
- Asigna nombres creativos desde el primer beat
- USA LOS MISMOS NOMBRES en todos los beats
- Ejemplos: "El Jakal", "Marcus", "La Doctora Chen"
</character_naming_rules>

<creative_storytelling>
NARRATIVA ATRAPANTE:
- Interpreta las escenas, no solo describas
- Inventa motivaciones y contexto emocional
- Agrega tensión y drama
- Conecta causas y consecuencias
- La narrativa debe sentirse como una historia completa, no fragmentos
</creative_storytelling>

<dramatic_pauses>
PAUSAS ESTRATÉGICAS - SILENCIO CINEMATOGRÁFICO:

Puedes agregar pausas dramáticas DESPUÉS de ciertos beats usando voiceover.pause_after_s.

CUÁNDO USAR PAUSAS (0.3-0.8 segundos):
✅ USAR pausa cuando:
- Cambio de escena importante o transición temporal
- Momento de suspense que requiere "respiración"
- Antes de un reveal o giro dramático
- Después de una frase impactante para dejar que "aterrice"
- Cierre de segmento narrativo antes de clímax

❌ NO usar pausa cuando:
- La acción es continua y rápida
- El diálogo fluye naturalmente al siguiente beat
- Ya hay espacio natural entre beats

DURACIÓN DE PAUSAS:
- 0.3s: Pausa breve (cambio de escena suave)
- 0.5s: Pausa media (suspense, transición)
- 0.8s: Pausa larga (momento muy dramático)

EJEMPLO:
Beat 1: "El Jakal ajusta el arma con precisión absoluta."
  → pause_after_s: 0.5 (dejar que la imagen del arma "respire")

Beat 2: "Marcus lo observa desde las sombras, esperando el momento perfecto."
  → pause_after_s: 0.0 (continúa fluidamente)

Beat 3: "El disparo rompe el silencio de la noche."
  → pause_after_s: 0.8 (pausa dramática después del clímax)

REGLA: Usa pausas con moderación. No más del 30% de los beats deben tener pausa.
</dramatic_pauses>

<output_schema>
ESTRUCTURA JSON REQUERIDA:
{{
  "overall": {{
    "hook": "Frase inicial atrapante (5-10 palabras)",
    "tone": "{style}",
    "full_narrative_script": "LA NARRATIVA COMPLETA aquí. Escribe toda la historia de principio a fin, ~{total_words_max} palabras. Esta es la versión completa y fluida de la historia."
  }},
  "beats": [
    {{
      "id": 1,
      "start_s": 0.0,
      "end_s": 7.2,
      "visual_summary": "Descripción breve de lo que se ve",
      "voiceover": {{
        "script": "SEGMENTO 1 de la narrativa completa.",
        "pause_after_s": 0.5
      }}
    }},
    {{
      "id": 2,
      "start_s": 7.2,
      "end_s": 14.5,
      "visual_summary": "Descripción breve de lo que se ve",
      "voiceover": {{
        "script": "SEGMENTO 2 de la narrativa. Continúa donde terminó el segmento 1.",
        "pause_after_s": 0.0
      }}
    }}
  ]
}}
</output_schema>

<critical_reminders>
1. overall.full_narrative_script = Historia completa (~{total_words_max} palabras)
2. beat[i].voiceover.script = Segmento i de esa historia
3. Segmentos deben fluir naturalmente: segmento1 + segmento2 + ... = narrativa completa
4. Cada segmento sincronizado con su beat visual
5. Tercera persona y nombres consistentes en TODO
6. Calcula palabras por beat: (duration) × {words_per_sec:.1f} × 0.85
</critical_reminders>
"""
    
    # Create model with unified system prompt
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        generation_config={"response_mime_type": "application/json", "temperature": 0.7},
        system_instruction=unified_system_prompt
    )
    
    # Make single API call
    try:
        response = model.generate_content([video_file, f"Analiza este video y genera la narrativa completa."])
        print(f"   ✅ Gemini response received ({len(response.text)} chars)")
        
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return VideoAnalysis()
    
    # Parse response
    import json
    try:
        cleaned_text = clean_json_response(response.text)
        result_data = json.loads(cleaned_text)
        
        # Handle different response structures
        if "VideoAnalysis" in result_data:
            result_data = result_data["VideoAnalysis"]
        
        # Ensure we have the beats array
        if "scenes" in result_data and "beats" not in result_data:
            result_data["beats"] = result_data.pop("scenes")
        
        # Debug: show first 3 beats
        if "beats" in result_data and len(result_data["beats"]) > 0:
            print(f"   📊 Generated {len(result_data['beats'])} beats")
            for i, beat in enumerate(result_data["beats"][:3]):
                print(f"   Beat {beat.get('id', i+1)}:")
                print(f"      Time: {beat.get('start_s', 0):.1f}s - {beat.get('end_s', 0):.1f}s")
                script = beat.get('voiceover', {}).get('script', '')
                print(f"      Script: {script[:80] if script else '(empty)'}...")
        
        # Construct VideoAnalysis
        return VideoAnalysis(**result_data)
        
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        print(f"   Raw response: {response.text[:500]}...")
        return VideoAnalysis()
