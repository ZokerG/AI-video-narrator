"""
Gemini AI Adapter - Implements IAIRepository interface
Wraps Gemini API for video analysis
"""
import google.generativeai as genai
from typing import Optional
import os
from src.domain.repositories.service_repositories import IAIRepository
from src.domain.entities.video_analysis import VideoAnalysis


class GeminiAdapter(IAIRepository):
    """Adapter for Google Gemini AI video analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini adapter
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=self.api_key)
    
    async def analyze_video(
        self,
        video_path: str,
        style: str,
        pace: str,
        voice_id: str,
        language: str = "es"
    ) -> VideoAnalysis:
        """
        Analyze video using Gemini AI
        
        Args:
            video_path: Path to video file
            style: Narrative style
            pace: Narrative pace
            voice_id: Voice ID for calibration
            language: Target language
            
        Returns:
            VideoAnalysis with narrative beats
        """
        # Import the actual implementation from infrastructure
        from src.infrastructure.ai.gemini_legacy import analyze_video_content  # ✅ Fixed: correct function name
        
        # Delegate to existing implementation
        analysis = analyze_video_content(
            video_path=video_path,
            style=style,
            pace=pace
        )
        
        return analysis
