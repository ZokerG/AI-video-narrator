"""
Repository interfaces - Abstract contracts for external services
Following the Dependency Inversion Principle
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from src.domain.entities.video_analysis import VideoAnalysis


class IAIRepository(ABC):
    """Interface for AI video analysis services (e.g., Gemini)"""
    
    @abstractmethod
    async def analyze_video(
        self,
        video_path: str,
        style: str,
        pace: str,
        voice_id: str,
        language: str = "es"
    ) -> VideoAnalysis:
        """
        Analyze video and generate narrative structure
        
        Args:
            video_path: Path to video file
            style: Narrative style (viral, documentary, etc.)
            pace: Narrative pace (slow, medium, fast)
            voice_id: Voice identifier for TTS
            language: Target language
            
        Returns:
            VideoAnalysis with beats and narrative
        """
        pass


class ITTSRepository(ABC):
    """Interface for Text-to-Speech services (e.g., ElevenLabs)"""
    
    @abstractmethod
    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        style: str,
        voice_settings: Optional[dict] = None
    ) -> Tuple[str, float]:
        """
        Generate audio from text
        
        Args:
            text: Script to convert to speech
            voice_id: Voice identifier
            style: Voice style/emotion
            voice_settings: Optional voice configuration
            
        Returns:
            Tuple of (audio_file_path, duration_seconds)
        """
        pass


class IVideoRepository(ABC):
    """Interface for video processing services (e.g., MoviePy)"""
    
    @abstractmethod
    async def mix_audio_with_video(
        self,
        video_path: str,
        audio_segments: list,
        output_path: str,
        original_volume: float = 0.0
    ) -> str:
        """
        Mix audio tracks with video
        
        Args:
            video_path: Path to source video
            audio_segments: List of audio segments with timing
            output_path: Path for output video
            original_volume: Original audio volume (0.0-1.0)
            
        Returns:
            Path to final video file
        """
        pass
    
    @abstractmethod
    def get_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        pass


class IStorageRepository(ABC):
    """Interface for file storage services (e.g., S3, MinIO)"""
    
    @abstractmethod
    async def upload_video(
        self,
        file_path: str,
        user_id: int,
        filename: str
    ) -> Tuple[str, str]:
        """
        Upload video to storage
        
        Args:
            file_path: Local file path
            user_id: User identifier
            filename: Destination filename
            
        Returns:
            Tuple of (storage_url, object_name)
        """
        pass
    
    @abstractmethod
    async def delete_video(self, object_name: str) -> bool:
        """Delete video from storage"""
        pass
