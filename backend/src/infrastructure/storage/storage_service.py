"""
Storage management layer for videos and audio files
Uses S3-compatible object storage (AWS S3 or MinIO)
"""
from src.infrastructure.storage.minio_storage import create_bucket_if_not_exists, upload_file, delete_file
from src.infrastructure.database.database import Video, AsyncSession, User
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict, Optional
import os

async def save_video_to_storage(
    user: User,
    video_path: str,
    session: AsyncSession,
    metadata: Dict
) -> Video:
    """
    Save video to S3/MinIO and create database record
    
    Args:
        user: User object
        video_path: Path to the video file
        session: Database session
        metadata: Additional metadata (voice_config, audio_config, etc.)
    
    Returns:
        Video database object
    """
    # Ensure bucket exists
    create_bucket_if_not_exists()
    
    # Create object name: users/{user_id}/videos/final_{timestamp}.mp4
    timestamp = int(datetime.utcnow().timestamp())
    object_name = f"users/{user.id}/videos/final_{timestamp}.mp4"
    
    # Upload to S3
    try:
        storage_data = upload_file(video_path, object_name)
    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        # Log error and potentially raise, but we might want to fail gracefully?
        # For now, raise so the API returns error
        raise e
    
    # Create video record in database
    video = Video(
        user_id=user.id,
        original_filename=metadata.get('original_filename', f'video_{timestamp}.mp4'),
        output_path=video_path,  # Keep local path for reference
        storage_object_name=storage_data['object_name'],
        storage_url=storage_data['url'],
        file_size=storage_data['file_size'],
        status='completed',
        voice_config=metadata.get('voice_config'),
        audio_config=metadata.get('audio_config'),
        completed_at=datetime.utcnow()
    )
    
    session.add(video)
    
    print(f"💾 Saved video to S3 for user {user.email} at {object_name}")
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
    Delete video from S3 and database
    
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
    
    # Delete from S3
    if video.storage_object_name:
        try:
            delete_file(video.storage_object_name)
        except Exception as e:
            print(f"Error deleting from S3: {e}")
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

async def save_video_to_drive(
    user: User,
    video_path: str,
    session: AsyncSession,
    metadata: Dict
) -> Video:
    """
    Async wrapper for save_video_to_storage
    (Kept name for backward compatibility if api.py still calls it)
    """
    return await save_video_to_storage(user, video_path, session, metadata)
