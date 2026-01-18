"""
Sistema de calibración para calcular words-per-second real por voz de ElevenLabs.

Este módulo mide la duración real del audio TTS generado y calcula la velocidad
exacta de narración (words per second) para cada voz, permitiendo cálculos
precisos de target_word_count.
"""
import os
import json
from typing import Dict, Optional

CALIBRATION_FILE = "core/voice_calibration.json"

# Textos de prueba para calibración
CALIBRATION_TEXTS = {
    "es": "Esta es una prueba de calibración diseñada específicamente para medir con precisión la velocidad exacta de narración de esta voz en español utilizando un texto de longitud moderada",
    "en": "This is a calibration test specifically designed to accurately measure the exact narration speed of this voice in English using a text of moderate length"
}

def load_calibrations() -> Dict:
    """Carga calibraciones guardadas desde el archivo JSON."""
    if os.path.exists(CALIBRATION_FILE):
        try:
            with open(CALIBRATION_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading calibrations: {e}")
    return {}

def save_calibrations(calibrations: Dict):
    """Guarda calibraciones al archivo JSON."""
    try:
        os.makedirs(os.path.dirname(CALIBRATION_FILE), exist_ok=True)
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(calibrations, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving calibrations: {e}")

def calibrate_voice(voice_id: str, language: str = "es", style: str = "viral") -> float:
    """
    Genera texto de prueba con la voz especificada, mide la duración real del audio,
    y calcula el WPS (words per second) exacto.
    
    Args:
        voice_id: ID de la voz de ElevenLabs
        language: Idioma del texto de prueba ("es" o "en")
        style: Estilo de narración para configuración de voz
    
    Returns:
        float: Words per second calculado
    """
    # Importar aquí para evitar dependencias circulares
    from core.tts import generate_audio_for_beat, get_audio_duration
    
    test_text = CALIBRATION_TEXTS.get(language, CALIBRATION_TEXTS["es"])
    word_count = len(test_text.split())
    
    print(f"🔬 Calibrando voz '{voice_id}' ({language}, {style})...")
    print(f"   📝 Texto de prueba: {word_count} palabras")
    
    # Generar audio de prueba
    test_file = f"outputs/_calibration_{voice_id}.mp3"
    
    try:
        result = generate_audio_for_beat(test_text, test_file, voice_id, style)
        
        # generate_audio_for_beat ahora retorna (path, duration) o None
        if result is None:
            print(f"   ❌ Error generando audio de calibración")
            return 2.3  # Fallback por defecto
        
        audio_path, duration = result
        
        if duration == 0:
            print(f"   ❌ Duración de audio es 0, usando fallback")
            return 2.3
        
        wps = word_count / duration
        print(f"   ✅ WPS calibrado: {wps:.2f} palabras/segundo")
        print(f"   ⏱️ Duración medida: {duration:.2f}s para {word_count} palabras")
        
        # Guardar calibración
        calibrations = load_calibrations()
        key = f"{voice_id}_{language}_{style}"
        calibrations[key] = {
            "wps": wps,
            "language": language,
            "style": style,
            "word_count": word_count,
            "duration": duration
        }
        save_calibrations(calibrations)
        
        # Limpiar archivo de prueba
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return wps
        
    except Exception as e:
        print(f"   ❌ Error durante calibración: {e}")
        import traceback
        traceback.print_exc()
        return 2.3  # Fallback

def get_wps_for_voice(voice_id: str, language: str = "es", style: str = "viral") -> float:
    """
    Obtiene WPS calibrado para una voz específica, o calibra si no existe.
    
    Args:
        voice_id: ID de la voz de ElevenLabs
        language: Idioma
        style: Estilo de narración
    
    Returns:
        float: Words per second para esta voz
    """
    calibrations = load_calibrations()
    key = f"{voice_id}_{language}_{style}"
    
    if key in calibrations:
        wps = calibrations[key]["wps"]
        print(f"   📊 Usando WPS calibrado: {wps:.2f} palabras/segundo")
        return wps
    
    print(f"   ⚠️ No hay calibración para {key}, calibrando ahora...")
    return calibrate_voice(voice_id, language, style)
