"""
ElevenLabs TTS Adapter - Implements ITTSRepository interface
Wraps ElevenLabs API for text-to-speech generation
"""
from typing import Tuple, Optional
import os
from src.domain.repositories.service_repositories import ITTSRepository


class ElevenLabsAdapter(ITTSRepository):
    """Adapter for ElevenLabs text-to-speech service"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ElevenLabs adapter
        
        Args:
            api_key: ElevenLabs API key (defaults to ELEVENLABS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found")
    
    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        style: str,
        voice_settings: Optional[dict] = None
    ) -> Tuple[str, float]:
        """
        Generate audio from text using ElevenLabs
        
        Args:
            text: Script to convert to speech
            voice_id: ElevenLabs voice ID
            style: Voice style/emotion
            voice_settings: Optional voice configuration (stability, similarity_boost)
            
        Returns:
            Tuple of (audio_file_path, duration_seconds)
        """
        # Import existing implementation
        from src.infrastructure.tts import generate_audio_for_beat
        
        # Delegate to existing implementation with correct parameter names
        result = generate_audio_for_beat(
            text=text,  # ✅ Correct parameter name
            output_path=f"src/temp/outputs/audio_temp_{hash(text)}.mp3",  # ✅ Correct parameter name
            voice_id=voice_id,
            style=style,
            voice_settings=voice_settings
        )
        
        if not result:
            raise Exception(f"Failed to generate audio for text: {text[:50]}...")
        
        audio_path, duration = result
        return (audio_path, duration)
