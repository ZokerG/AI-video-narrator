"""
Analysis Router V2 - Using Clean Architecture Use Cases
This version uses dependency injection and AnalyzeVideoUseCase
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time
import os

# Import from core (for auth and DB only)
from src.infrastructure.database import get_db_session, User
from src.infrastructure.auth import get_current_user

# Import use case and dependencies
from src.application.use_cases.analyze_video_use_case import (
    AnalyzeVideoUseCase,
    AnalyzeVideoRequest
)
from src.presentation.api.dependencies import get_analyze_video_use_case

router = APIRouter(tags=["analysis"])


@router.post("/analyze-v2")
async def analyze_video_v2(
    video: UploadFile = File(...),  # ✅ Changed from 'file' to 'video' to match frontend
    style: str = Form("viral"),
    pace: str = Form("medium"),
    voice_id: Optional[str] = Form(None),
    stability: int = Form(50),  # ✅ Added voice settings
    similarity_boost: int = Form(75),
    speed: int = Form(100),
    original_volume: int = Form(10),  # ✅ Changed to int to match frontend
    background_track: Optional[str] = Form(None),  # ✅ Changed from background_music_file
    background_volume: int = Form(10),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    use_case: AnalyzeVideoUseCase = Depends(get_analyze_video_use_case)
):
    """
    Analyze video using Clean Architecture (NEW VERSION)
    Uses AnalyzeVideoUseCase with dependency injection
    """
    # Check credits
    if current_user.credits <= 0:
        raise HTTPException(400, "Insufficient credits")
    
    # Save uploaded file
    file_path = f"src/temp/uploads/{int(time.time())}_{video.filename}"
    with open(file_path, "wb") as f:
        content = await video.read()
        f.write(content)
    
    print(f"[{time.strftime('%X')}] 💾 Video saved: {file_path}")
    
    try:
        # Create request DTO
        request = AnalyzeVideoRequest(
            video_path=file_path,
            user_id=current_user.id,
            style=style,
            pace=pace,
            voice_id=voice_id,
            language="es",
            original_volume=original_volume / 100.0,  # Convert percentage to decimal
            background_music_path=f"src/assets/music/{background_track}" if background_track else None,
            session=session  # ✅ Pass DB session for saving video record
        )
        
        # Execute use case
        print(f"[{time.strftime('%X')}] 🚀 Executing AnalyzeVideoUseCase...")
        response = await use_case.execute(request)
        
        if not response.success:
            raise HTTPException(500, response.error or "Analysis failed")
        
        # Deduct credits
        current_user.credits -= 1
        await session.commit()
        
        print(f"[{time.strftime('%X')}] ✅ Analysis complete!")
        
        return {
            "status": "completed",
            "analysis": response.analysis.model_dump() if response.analysis else None,
            "storage_url": response.storage_url,
            "output_video": response.final_video_path,
            "video_id": None  # TODO: Save to database
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Processing failed: {str(e)}")


# Keep old endpoint for backward compatibility
@router.post("/analyze")
async def analyze_video_legacy(
    file: UploadFile = File(...),
    style: str = Form("viral"),
    pace: str = Form("medium"),
    voice_id: Optional[str] = Form(None),
    original_volume: float = Form(0.0),
    background_music_file: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    LEGACY: Old implementation for backward compatibility
    Redirects to new clean architecture version
    """
    use_case = get_analyze_video_use_case()
    return await analyze_video_v2(
        file=file,
        style=style,
        pace=pace,
        voice_id=voice_id,
        original_volume=original_volume,
        background_music_file=background_music_file,
        current_user=current_user,
        session=session,
        use_case=use_case
    )
