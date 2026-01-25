import os
from elevenlabs import ElevenLabs, VoiceSettings
from moviepy import AudioFileClip
from typing import Optional, Tuple

def get_audio_duration(audio_path: str) -> float:
    """
    Mide la duración real de un archivo de audio MP3.
    
    Args:
        audio_path: Ruta al archivo MP3
    
    Returns:
        float: Duración en segundos
    """
    try:
        audio = AudioFileClip(audio_path)
        duration_s = audio.duration
        audio.close()
        return duration_s
    except Exception as e:
        print(f"   ⚠️ Error midiendo duración de audio: {e}")
        return 0.0

def get_voice_settings(style: str = "viral") -> VoiceSettings:
    """
    Obtiene la configuración óptima de voz para ElevenLabs según el estilo.
    
    Args:
        style: Estilo de narración ("viral", "documentary", "funny")
    
    Returns:
        VoiceSettings: Configuración de voz optimizada
    """
    settings_by_style = {
        "viral": {
            "stability": 0.4,         # Más expresivo y dinámico
            "similarity_boost": 0.7,  # Mantener características naturales
            "style": 0.0,             # Sin énfasis adicional de estilo
            "use_speaker_boost": True
        },
        "documentary": {
            "stability": 0.6,         # Más estable y consistente
            "similarity_boost": 0.75, # Mayor claridad
            "style": 0.0,
            "use_speaker_boost": True
        },
        "funny": {
            "stability": 0.3,         # Muy expresivo y variable
            "similarity_boost": 0.7,  # Natural
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    settings_dict = settings_by_style.get(style, settings_by_style["viral"])
    return VoiceSettings(**settings_dict)

def generate_audio_for_beat(
    text: str, 
    output_path: str, 
    voice_id: str = None,
    style: str = "viral",
    voice_settings: dict = None
) -> Optional[Tuple[str, float]]:
    """
    Genera audio para un texto usando ElevenLabs y mide su duración real.
    
    Args:
        text: Texto a convertir en audio
        output_path: Ruta donde guardar el archivo MP3
        voice_id: ID de la voz de ElevenLabs (si None, usa variable de entorno)
        style: Estilo de narración para configuración de voz (solo si voice_settings es None)
        voice_settings: Dict con stability, similarity_boost, speed personalizados
    
    Returns:
        Tuple[str, float]: (ruta del archivo, duración en segundos) o None si falla
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            print("❌ ERROR: ELEVENLABS_API_KEY not set. Skipping audio generation.")
            return None
        
        # Usar voice_id de variable de entorno si no se especifica
        if voice_id is None:
            voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")

        print(f"   🎤 Generating TTS ({style}): '{text[:50]}...'")
        client = ElevenLabs(api_key=api_key)

        # Usar voice_settings custom o configuración por estilo
        if voice_settings:
            settings = VoiceSettings(
                stability=voice_settings.get("stability", 0.5),
                similarity_boost=voice_settings.get("similarity_boost", 0.75),
                style=voice_settings.get("style_exaggeration", 0.0),
                use_speaker_boost=True
            )
            print(f"   🎛️ Custom settings: stability={voice_settings.get('stability'):.2f}, similarity={voice_settings.get('similarity_boost'):.2f}")
        else:
            # Fallback a configuración por estilo
            settings = get_voice_settings(style)

        # Generar audio con configuración optimizada
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            voice_settings=settings
        )

        # Convertir generador a bytes
        audio_bytes = b"".join(audio_generator)
        
        # Asegurar que existe el directorio
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Guardar archivo
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        # Medir duración real
        duration = get_audio_duration(output_path)
        
        print(f"   ✅ Saved: {output_path} ({len(audio_bytes)} bytes, {duration:.2f}s)")
        return (output_path, duration)
    
    except Exception as e:
        print(f"   ❌ ERROR generating TTS for text '{text[:30]}...': {str(e)}")
        import traceback
        traceback.print_exc()
        return None

