"""
Voices Router - Voice management and preview endpoints
"""
from fastapi import APIRouter, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

router = APIRouter(prefix="/voices", tags=["voices"])
audio_router = APIRouter(prefix="/audio", tags=["audio"])


@router.get("/")
async def get_available_voices():
    """Get list of available ElevenLabs voices"""
    try:
        from elevenlabs import ElevenLabs
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise HTTPException(500, "ElevenLabs API key not configured")
        
        client = ElevenLabs(api_key=api_key)
        voices_response = client.voices.get_all()
        
        voices = [
            {
                "id": voice.voice_id,  # ✅ Frontend expects "id"
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": getattr(voice, "category", "general"),
                "description": getattr(voice, "description", ""),
                "labels": getattr(voice, "labels", {}),  # ✅ Include labels
                "preview_url": getattr(voice, "preview_url", None)
            }
            for voice in voices_response.voices
        ]
        
        return {"voices": voices}
    
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch voices: {str(e)}")


@router.post("/preview")
async def preview_voice(
    voice_id: str = Form(...),
    text: str = Form("Hola, esta es una muestra de mi voz narrando un video viral.")  # ✅ Changed to "text"
):
    """Generate audio preview for a voice"""
    try:
        from src.infrastructure.tts import generate_audio_for_beat
        import time
        
        output_path = f"src/temp/outputs/preview_{voice_id}_{int(time.time())}.mp3"
        
        result = generate_audio_for_beat(
            text=text,  # ✅ Use text parameter
            output_path=output_path,
            voice_id=voice_id,
            style="viral"
        )
        
        if not result:
            raise HTTPException(500, "Failed to generate preview")
        
        audio_path, duration = result
        
        # ✅ Return proper URL - outputs is mounted at /outputs
        # audio_path is like "outputs/preview_xxx.mp3"
        # We need to return "/outputs/preview_xxx.mp3"
        url_path = audio_path.replace("\\", "/")  # Handle Windows paths
        if not url_path.startswith("/"):
            url_path = "/" + url_path
        
        return {
            "audio_url": url_path,
            "duration": duration,
            "voice_id": voice_id
        }
    
    except Exception as e:
        raise HTTPException(500, f"Preview failed: {str(e)}")


@audio_router.get("/background-tracks")
async def get_background_tracks():
    """Get list of available background music tracks"""
    music_dir = "src/assets/music"
    
    if not os.path.exists(music_dir):
        return {"tracks": []}
    
    tracks = [
        {
            "id": f,  # ✅ Added id field (same as filename)
            "filename": f,
            "name": f.replace(".mp3", "").replace("_", " ").title(),
            "url": f"/audio/assets/{f}"
        }
        for f in os.listdir(music_dir)
        if f.endswith(".mp3")
    ]
    
    return {"tracks": tracks}
