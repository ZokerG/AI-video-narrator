"""
Generate Reel Script Use Case
Generates viral short video script using AI
"""
from dataclasses import dataclass
from typing import Optional
from src.domain.repositories.service_repositories import IAIRepository


@dataclass
class GenerateReelScriptRequest:
    """Request to generate reel script"""
    topic: str
    user_id: int
    style: str = "viral"  # viral, curious, funny
    duration: int = 30    # seconds


@dataclass
class GenerateReelScriptResponse:
    """Response with generated script"""
    success: bool
    script: Optional[dict] = None  # Contains scenes with narration, visual_query, duration
    error: Optional[str] = None


class GenerateReelScriptUseCase:
    """
    Use Case: Generate viral reel script from topic
    
    Workflow:
    1. Use AI to generate structured script
    2. Return scenes with narration and visual queries
    """
    
    def __init__(self, ai_repository: IAIRepository):
        self.ai = ai_repository
    
    async def execute(self, request: GenerateReelScriptRequest) -> GenerateReelScriptResponse:
        """
        Generate reel script from topic
        
        Args:
            request: Script generation request
            
        Returns:
            GenerateReelScriptResponse with script data
        """
        try:
            print(f"[GenerateReelScript] Generating script for topic: {request.topic}")
            
            # Delegate to AI repository (wraps core.content_generator)
            from src.infrastructure.ai.content_generator import generate_reels_script
            
            script = generate_reels_script(
                topic=request.topic,
                style=request.style
            )
            
            if not script or not script.get('scenes'):
                return GenerateReelScriptResponse(
                    success=False,
                    error="AI failed to generate valid script"
                )
            
            print(f"[GenerateReelScript] ✅ Generated {len(script.get('scenes', []))} scenes")
            
            return GenerateReelScriptResponse(
                success=True,
                script=script
            )
            
        except Exception as e:
            print(f"[GenerateReelScript] ❌ Error: {str(e)}")
            return GenerateReelScriptResponse(
                success=False,
                error=str(e)
            )
