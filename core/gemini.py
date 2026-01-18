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
    Two-stage pipeline:
    1. Visual Analysis (Gemini Vision) -> What is happening?
    2. Script Generation (Gemini Text) -> What should we say?
    """
    # 1. Upload
    video_file = upload_to_gemini(video_path)
    wait_for_files_active([video_file])

    # --- STAGE 1: VISUAL ANALYSIS ---
    print("   ↳ 👁️ Stage 1: Visual Analysis...")
    
    visual_system_prompt = """
<role>Eres un editor profesional de video especializado en segmentación visual.</role>

<task>
Analiza el video frame-by-frame y divídelo en "beats" visuales basándote en:
- Cambios de escena o corte de cámara
- Cambios significativos de ángulo
- Eventos visuales importantes o acciones clave
</task>

<constraints>
- Cada beat DEBE tener timecodes precisos al décimo de segundo (e.g., 3.2, no 3)
- La descripción visual DEBE ser concisa (máximo 12 palabras)
- Los beats NO deben solaparse (end_s de beat N = start_s de beat N+1)
- Numera los beats secuencialmente empezando en 1
- Devuelve ÚNICAMENTE JSON válido, sin texto adicional antes o después
</constraints>

<output_schema>
[
  {
    "id": <número entero>,
    "start_s": <decimal>,
    "end_s": <decimal>,
    "visual_description": "<descripción concisa de lo que ocurre visualmente>"
  }
]
</output_schema>
"""
    
    model_vision = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={"response_mime_type": "application/json", "temperature": 0.2},
        system_instruction=visual_system_prompt
    )
    
    # Prompt based on pace
    pace_instructions = {
        "fast": "Divide el video en beats cortos de 2-5 segundos para ritmo frenético.",
        "medium": "Divide el video en beats de 5-10 segundos para ritmo moderado.",
        "slow": "Divide el video en beats largos de 10-20 segundos para ritmo calmado."
    }
    pace_prompt = pace_instructions.get(pace, pace_instructions["fast"])
    
    response_vision = model_vision.generate_content([video_file, pace_prompt])
    print(f"   RAW Stage 1 Output: {response_vision.text[:200]}...") # Debug log
    
    import json
    try:
        visual_data = json.loads(clean_json_response(response_vision.text))
        # Sort by start time just in case
        visual_data.sort(key=lambda x: x.get('start_s', 0))
    except Exception as e:
        print(f"Error parsing Stage 1: {e}")
        print(f"Full Stage 1 Response: {response_vision.text}")
        return VideoAnalysis()

    # --- STAGE 2: SCRIPT GENERATION ---
    print(f"   ↳ ✍️ Stage 2: Scripting ({len(visual_data)} beats)...")
    
    # Calculate word constraints using calibrated WPS
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")  # Voz desde .env
    words_per_sec = get_wps_for_voice(voice_id, language="es", style=style)
    
    enriched_visuals = []
    for v in visual_data:
        duration = v.get('end_s', 0) - v.get('start_s', 0)
        
        # MEJORA: Manejo de silencios estratégicos para beats muy cortos
        if duration < 1.5:
            target_words = 0  # Forzar silencio para micro-cortes (más inmersivo)
        else:
            # Usar WPS calibrado para calcular palabras objetivo
            target_words = max(5, int(duration * words_per_sec * 0.85))  # 85% para evitar cortes
        
        v['target_word_count'] = target_words
        v['duration_s'] = duration
        enriched_visuals.append(v)
    
    print(f"   📊 Using calibrated WPS: {words_per_sec:.2f} words/second")
    
    from core.prompts import get_system_instruction
    script_system_instruction = get_system_instruction(style, pace)
    
    import json
    
    # Determinar instrucciones de POV según estilo
    pov_instructions = {
        "viral": """MODO ACTUACIÓN INMERSIVA:
- Tú ERES el protagonista. Usa primera persona: "Yo", "Me", "Mi"
- NO digas "Veo un teléfono". DI: "El teléfono sonó y mi corazón se detuvo"
- REACCIONA emocionalmente a lo que pasa, no lo describas como comentarista
- Habla como si ESTUVIERAS VIVIENDO el momento, no observándolo""",
        "documentary": """MODO NARRADOR DOCUMENTAL:
- Usa tercera persona objetiva y tono profesional
- Describe con precisión pero mantén interés narrativo
- Contexto histórico o científico cuando sea relevante""",
        "funny": """MODO COMEDIANTE:
- Usa primera persona con perspectiva humorística
- Haz observaciones sarcásticas o absurdas sobre lo que pasa
- Timing cómico: las pausas también pueden ser chistes"""
    }
    
    pov_instruction = pov_instructions.get(style, pov_instructions["viral"])
    
    script_prompt = f"""
<context>
Tienes una lista de beats visuales extraídos del video.
Cada beat tiene:
- visual_description: qué está pasando
- duration_s: duración del beat en segundos
- target_word_count: PALABRAS EXACTAS que debes escribir para llenar el tiempo
</context>

<input>
Visual Beats:
{json.dumps(enriched_visuals, indent=2)}
</input>

<critical_timing_rules>
1. El 'target_word_count' fue calculado científicamente basado en la voz real
2. DEBES escribir EXACTAMENTE esa cantidad de palabras (±2 palabras máximo)
3. Ejemplo: beat de 5s con target=12 → escribe entre 10-14 palabras
4. Si target_word_count = 0, deja el script VACÍO (silencio estratégico)
5. NUNCA fuerces palabras en beats muy cortos si target=0
</critical_timing_rules>

<narrative_quality_rules>
{pov_instruction}

1. USA CONECTORES para fluidez narrativa: "Después...", "De repente...", "Pero entonces..."
2. La narración debe fluir como UNA historia continua, no frases sueltas
3. NO describas TODO, solo momentos importantes que generan emoción
4. GÉNERO: Estilo {style} - mantén el tono consistente
5. TIMING es SAGRADO: respeta el conteo de palabras o el audio se cortará
</narrative_quality_rules>

<output_structure>
Devuelve JSON en esta estructura EXACTA:
{{
  "overall": {{
    "hook": "<gancho inicial de 1 frase que enganche al espectador>",
    "one_sentence_summary": "<resumen de 1 frase de todo el video>",
    "tone": "<tono usado: {style}>"
  }},
  "beats": [
    {{
      "id": <mismo id del visual beat>,
      "visual_summary": "<descripción de qué está pasando visualmente>",
      "key_visuals": ["<tag visual 1>", "<tag visual 2>"],
      "voiceover": {{
        "script": "<NARRACIÓN COMPLETA con target_word_count palabras>"
      }}
    }}
  ]
}}
</output_structure>

<examples>
Ejemplo de beat bien hecho:
Input: {{"id": 1, "duration_s": 5.0, "target_word_count": 12, "visual_description": "Hombre corriendo por la playa"}}
Output: {{"id": 1, "voiceover": {{"script": "Mira cómo este atleta corre con una técnica impresionante y una velocidad que te deja sin aliento"}}}}
Palabras: 14 ✓ (dentro del rango 10-14)

Ejemplo de beat MAL hecho (muy corto):
Input: {{"id": 1, "duration_s": 5.0, "target_word_count": 12}}
Output: {{"id": 1, "voiceover": {{"script": "Qué increíble"}}}}
Palabras: 2 ❌ (causará silencio!)
</examples>

<critical>
IMPORTANTE: 
- La clave DEBE ser "beats", NO "scenes"
- DEBES devolver exactamente el mismo 'id' para cada beat provisto en el input
- NO fusiones beats ni cambies el orden
- NO inventes beats adicionales
- Respeta el número exacto de beats del INPUT
</critical>
"""
    
    model_text = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={"response_mime_type": "application/json", "temperature": 0.7},
        system_instruction=script_system_instruction
    )
    
    response_text = model_text.generate_content(script_prompt)
    print(f"   RAW Stage 2 Output: {response_text.text[:200]}...") # Debug log
    
    try:
        final_data = json.loads(clean_json_response(response_text.text))
        
        # Handle case where Gemini wraps response in "VideoAnalysis" key
        if 'VideoAnalysis' in final_data:
            print("   ⚠️ Unwrapping 'VideoAnalysis' wrapper...")
            final_data = final_data['VideoAnalysis']
        
        # Handle both 'beats' and 'scenes' keys (Gemini sometimes uses different naming)
        beats_data = None
        if 'beats' in final_data:
            beats_data = final_data['beats']
            print(f"   📝 Found {len(beats_data)} beats in Stage 2 response")
        elif 'scenes' in final_data:
            beats_data = final_data['scenes']
            print(f"   📝 Found {len(beats_data)} scenes (renaming to beats)")
            final_data['beats'] = beats_data
        else:
            print(f"   ⚠️ WARNING: No 'beats' or 'scenes' key found in Stage 2 response!")
            print(f"   Available keys: {list(final_data.keys())}")
        
        # MEJORA: Mapeo basado en ID, no en índice (evita desincronización)
        # Crear diccionario de búsqueda para los visuales
        visual_lookup = {v['id']: v for v in visual_data}
        
        if beats_data:
            final_beats = []
            for beat in beats_data:
                beat_id = beat.get('id')
                # Usar ID para buscar, no la posición en la lista
                if beat_id and beat_id in visual_lookup:
                    v_beat = visual_lookup[beat_id]
                    # Copiar timestamps ESTRICTOS del análisis visual (Stage 1)
                    beat['start_s'] = v_beat['start_s']
                    beat['end_s'] = v_beat['end_s']
                    final_beats.append(beat)
                else:
                    print(f"   ⚠️ Warning: Beat ID {beat_id} not found in visual data")
            
            print(f"   ✅ Mapped {len(final_beats)} beats successfully")
            final_data['beats'] = final_beats
            
        return VideoAnalysis(**final_data)
        
    except Exception as e:
        print(f"Error parsing Stage 2: {e}")
        print(f"Full Stage 2 Response: {response_text.text}")
        
        # --- FALLBACK MECHANISM ---
        # If Stage 2 fails, we shouldn't return empty. We should use Stage 1 visuals.
        print("⚠️ Stage 2 Failed. Falling back to Stage 1 Visuals.")
        
        fallback_beats = []
        for v in visual_data:
            fallback_beats.append({
                "id": v.get("id"),
                "start_s": v.get("start_s"),
                "end_s": v.get("end_s"),
                "visual_summary": v.get("visual_description", ""),
                "key_visuals": [],
                "voiceover": {
                    "script": v.get("visual_description", "Scene without narration."),
                    "subtitle": ""
                }
            })
            
        return VideoAnalysis(
            duration_s=0.0,
            overall={
                "hook": "Fallback Analysis",
                "one_sentence_summary": "We encountered an error generating the creative script, but here is the visual breakdown.",
                "tone": "Technique"
            },
            beats=fallback_beats
        )
