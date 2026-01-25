"""
Videos Router - Video management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel

# Import from core (temporary)
from src.infrastructure.database import get_db_session, User
from src.infrastructure.auth import get_current_user
from src.infrastructure.storage.storage_service import get_user_videos, delete_video

router = APIRouter(prefix="/videos", tags=["videos"])

# Schemas
class VideoResponse(BaseModel):
    id: int
    original_filename: str
    storage_url: str
    status: str
    created_at: str


@router.get("/my-videos")
async def get_my_videos(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get all videos for current user"""
    videos = await get_user_videos(current_user.id, session)
    
    return {
        "videos": [
            {
                "id": v.id,
                "original_filename": v.original_filename,
                "storage_url": v.storage_url,
                "file_size": v.file_size,
                "status": v.status,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "completed_at": v.completed_at.isoformat() if v.completed_at else None,
            }
            for v in videos
        ]
    }


@router.delete("/{video_id}")
async def delete_user_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a video"""
    success = await delete_video(video_id, current_user.id, session)
    
    if not success:
        raise HTTPException(status_code=404, detail="Video not found or access denied")
    
    return {"message": "Video deleted successfully"}
