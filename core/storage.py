"""
Storage management layer for videos and audio files
Abstracts local and Google Drive storage
"""
from core.drive import get_or_create_user_folder, upload_file, delete_file
from core.database import Video, AsyncSession, User
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict, Optional
import os

async def save_video_to_drive(
    user: User,
    video_path: str,
    session: AsyncSession,
    metadata: Dict
) -> Video:
    """
    Save video to Google Drive and create database record
    
    Args:
        user: User object
        video_path: Path to the video file
        session: Database session
        metadata: Additional metadata (voice_config, audio_config, etc.)
    
    Returns:
        Video database object
    """
    # Get or create user folder structure in Drive
    folders = get_or_create_user_folder(user.email)
    
    # Update user's drive_folder_id if not set
    if not user.google_drive_folder_id:
        user.google_drive_folder_id = folders['user_folder_id']
        session.add(user)
    
    # Upload video to Drive
    file_name = f"video_{int(datetime.utcnow().timestamp())}_final.mp4"
    drive_data = upload_file(
        file_path=video_path,
        folder_id=folders['outputs_folder_id'],
        file_name=file_name
    )
    
    # Create video record in database
    video = Video(
        user_id=user.id,
        original_filename=metadata.get('original_filename', file_name),
        output_path=video_path,  # Keep local path for now
        drive_file_id=drive_data['file_id'],
        drive_link=drive_data['download_link'],
        file_size=drive_data['file_size'],
        status='completed',
        voice_config=metadata.get('voice_config'),
        audio_config=metadata.get('audio_config'),
        completed_at=datetime.utcnow()
    )
    
    session.add(video)
    await session.flush()
    await session.refresh(video)
    
    print(f"💾 Saved video to Drive for user {user.email}")
    return video

async def get_user_videos(user_id: int, session: AsyncSession) -> List[Video]:
    """Get all videos for a user"""
    result = await session.execute(
        select(Video)
        .where(Video.user_id == user_id)
        .order_by(Video.created_at.desc())
    )
    return list(result.scalars().all())

async def delete_video(video_id: int, user_id: int, session: AsyncSession) -> bool:
    """
    Delete video from Drive and database
    
    Returns True if successful, False otherwise
    """
    # Get video from database
    result = await session.execute(
        select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id  # Ensure user owns the video
        )
    )
    video = result.scalar_one_or_none()
    
    if not video:
        return False
    
    # Delete from Drive
    if video.drive_file_id:
        try:
            delete_file(video.drive_file_id)
        except Exception as e:
            print(f"Error deleting from Drive: {e}")
            # Continue anyway to remove from DB
    
    # Delete local file if exists
    if video.output_path and os.path.exists(video.output_path):
        try:
            os.remove(video.output_path)
        except Exception as e:
            print(f"Error deleting local file: {e}")
    
    # Delete from database
    await session.delete(video)
    
    print(f"🗑️ Deleted video {video_id} for user {user_id}")
    return True
