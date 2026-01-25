"""
Reels Router - Viral short video generation endpoints
Uses Clean Architecture with dependency injection
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from src.infrastructure.database import get_db_session, User
from src.infrastructure.auth import get_current_user

from src.application.use_cases.generate_reel_script_use_case import (
    GenerateReelScriptUseCase,
    GenerateReelScriptRequest
)
from src.application.use_cases.create_reel_use_case import (
    CreateReelUseCase,
    CreateReelRequest
)
from src.presentation.api.dependencies import (
    get_generate_reel_script_use_case,
    get_create_reel_use_case
)

router = APIRouter(prefix="/reels", tags=["reels"])


class ScriptRequest(BaseModel):
    """Request model for script generation"""
    topic: str
    style: str = "viral"
    duration: int = 30


class ReelCreationRequest(BaseModel):
    """Request model for reel creation"""
    script: dict
    voice_id: str
    bg_music: Optional[str] = None


@router.post("/generate-script")
async def generate_reel_script(
    request: ScriptRequest,
    current_user: User = Depends(get_current_user),
    use_case: GenerateReelScriptUseCase = Depends(get_generate_reel_script_use_case)
):
    """
    Generate viral reel script using AI
    
    Creates structured script with scenes, narration, and visual queries
    """
    print(f"[Reels] Generating script for topic: {request.topic}")
    
    response = await use_case.execute(
        GenerateReelScriptRequest(
            topic=request.topic,
            user_id=current_user.id,
            style=request.style,
            duration=request.duration
        )
    )
    
    if not response.success:
        raise HTTPException(500, response.error or "Script generation failed")
    
    return {
        "status": "success",
        "script": response.script
    }


@router.post("/create")
async def create_reel(
    request: ReelCreationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    use_case: CreateReelUseCase = Depends(get_create_reel_use_case)
):
    """
    Create viral reel video from script
    
    Workflow:
    1. Generate TTS audio for each scene
    2. Download images from Pexels
    3. Assemble video with Ken Burns effect
    4. Add background music
    5. Upload to storage
    """
    # Check credits
    REEL_COST = 20
    if current_user.credits < REEL_COST:
        raise HTTPException(403, "Insufficient credits")
    
    print(f"[Reels] Creating reel for user {current_user.id}")
    
    response = await use_case.execute(
        CreateReelRequest(
            script=request.script,
            voice_id=request.voice_id,
            user_id=current_user.id,
            bg_music=request.bg_music
        )
    )
    
    if not response.success:
        raise HTTPException(500, response.error or "Reel creation failed")
    
    # ✅ Save video record to database
    from src.infrastructure.database import Video
    from datetime import datetime
    
    # Extract filename from storage URL or use a default
    filename = response.storage_url.split("/")[-1].split("?")[0] if response.storage_url else "reel.mp4"
    
    new_video = Video(
        user_id=current_user.id,
        original_filename=filename,  # ✅ Correct field name
        storage_url=response.storage_url,
        storage_object_name=f"users/{current_user.id}/videos/{filename}",
        status="completed",
        completed_at=datetime.utcnow()
    )
    session.add(new_video)
    
    # Deduct credits
    current_user.credits -= REEL_COST
    await session.commit()
    
    print(f"[Reels] ✅ Video saved to DB with id={new_video.id}")
    
    return {
        "status": "completed",
        "storage_url": response.storage_url,
        "video_id": new_video.id,
        "credits_remaining": current_user.credits
    }
