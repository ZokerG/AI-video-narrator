"""
MoviePy Video Processor Adapter - Implements IVideoRepository interface
Wraps MoviePy for video processing operations
"""
from typing import List, Dict
from src.domain.repositories.service_repositories import IVideoRepository


class MoviePyAdapter(IVideoRepository):
    """Adapter for MoviePy video processing"""
    
    def __init__(self):
        """Initialize MoviePy adapter"""
        pass
    
    async def mix_audio_with_video(
        self,
        video_path: str,
        audio_segments: List[Dict],
        output_path: str,
        original_volume: float = 0.0
    ) -> str:
        """
        Mix audio tracks with video using MoviePy
        
        Args:
            video_path: Path to source video
            audio_segments: List of dicts with 'path', 'start_s', 'duration', 'pause_after'
            output_path: Path for output video
            original_volume: Original audio volume (0.0-1.0)
            
        Returns:
            Path to final video file
        """
        # Import existing implementation
        from src.infrastructure.video import mix_audio_with_video  # ✅ Correct function name
        
        # Delegate to existing implementation
        result = mix_audio_with_video(
            video_path=video_path,
            audio_map=audio_segments,
            output_path=output_path,
            keep_original_audio=True,
            original_volume_factor=original_volume
        )
        
        # Ensure we return the output path (function might return None)
        return result if result else output_path  # ✅ Fallback to output_path if None
    
    def get_duration(self, video_path: str) -> float:
        """
        Get video duration in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(video_path) as clip:
                return clip.duration
        except Exception:
            # Fallback if MoviePy fails
            return 0.0
