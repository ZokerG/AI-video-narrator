"""
Create Reel Use Case
Orchestrates complete reel video creation workflow
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from pathlib import Path
import time
import uuid

from src.domain.repositories.service_repositories import (
    ITTSRepository,
    IVideoRepository,
    IStorageRepository
)
from src.domain.repositories.image_repository import IImageRepository


@dataclass
class CreateReelRequest:
    """Request to create reel video"""
    script: dict  # Contains scenes with narration, visual_query, duration
    voice_id: str
    user_id: int
    bg_music: Optional[str] = None


@dataclass
class CreateReelResponse:
    """Response with created reel"""
    success: bool
    video_id: Optional[int] = None
    storage_url: Optional[str] = None
    local_path: Optional[str] = None
    error: Optional[str] = None


class CreateReelUseCase:
    """
    Use Case: Create complete reel video from script
    
    Workflow:
    1. Generate TTS audio for each scene
    2. Download images from Pexels for each scene
    3. Assemble video with Ken Burns effect
    4. Add background music
    5. Upload to storage
    """
    
    def __init__(
        self,
        tts_repository: ITTSRepository,
        image_repository: IImageRepository,
        video_repository: IVideoRepository,
        storage_repository: IStorageRepository
    ):
        self.tts = tts_repository
        self.images = image_repository
        self.video = video_repository
        self.storage = storage_repository
    
    async def execute(self, request: CreateReelRequest) -> CreateReelResponse:
        """
        Create reel video from script
        
        Args:
            request: Reel creation request
            
        Returns:
            CreateReelResponse with video URL
        """
        try:
            # Create job directory
            job_id = f"reel_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            job_dir = Path(f"src/temp/outputs/{job_id}")
            job_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"[CreateReel] Starting job {job_id}")
            
            scenes = request.script.get('scenes', [])
            if not scenes:
                return CreateReelResponse(
                    success=False,
                    error="Script contains no scenes"
                )
            
            # Step 1 & 2: Generate audio and download images
            print(f"[CreateReel] Processing {len(scenes)} scenes...")
            audio_map = []
            processed_scenes = []
            current_time = 0.0
            
            for i, scene in enumerate(scenes):
                # Generate TTS
                narration = scene.get('narration', '')
                if narration:
                    audio_path, duration = await self.tts.generate_audio(
                        text=narration,
                        voice_id=request.voice_id,
                        style="viral"
                    )
                    
                    audio_map.append({
                        'path': audio_path,
                        'start_s': current_time,
                        'duration': duration
                    })
                    
                    scene['duration_estimate'] = duration
                    current_time += duration
                
                # Download image
                visual_query = scene.get('visual_query')
                image_path = job_dir / f"image_{i}.jpg"
                
                if visual_query:
                    image_url = await self.images.search_image(visual_query)
                    if image_url:
                        await self.images.download_image(str(image_url), str(image_path))
                        scene['image_path'] = str(image_path)
                
                processed_scenes.append(scene)
            
            # Step 3: Assemble video
            print(f"[CreateReel] Assembling video...")
            final_filename = f"final_{job_id}.mp4"
            final_path = job_dir / final_filename
            
            # Delegate to existing reel creation
            from src.infrastructure.video import create_reel_video
            
            bg_track_path = None
            if request.bg_music:
                bg_track_path = f"src/assets/music/{request.bg_music}"
            
            create_reel_video(
                scenes=processed_scenes,
                audio_map=audio_map,
                output_path=str(final_path),
                background_track=bg_track_path
            )
            
            # Step 4: Upload to storage
            print(f"[CreateReel] Uploading to storage...")
            storage_url, object_name = await self.storage.upload_video(
                file_path=str(final_path),
                user_id=request.user_id,
                filename=final_filename
            )
            
            # Step 5: Cleanup ALL temporary files
            print(f"[CreateReel] Cleaning up temporary files...")
            try:
                import shutil
                import os
                
                # Remove audio files (may be outside job_dir in outputs/)
                for audio_info in audio_map:
                    audio_path = audio_info.get('path', '')
                    if audio_path and os.path.exists(audio_path):
                        os.remove(audio_path)
                        print(f"   ✅ Removed audio: {audio_path}")
                
                # Remove job directory (images, final video)
                if job_dir.exists():
                    shutil.rmtree(job_dir)
                    print(f"   ✅ Removed job dir: {job_dir}")
                    
            except Exception as e:
                print(f"[CreateReel] ⚠️ Cleanup warning: {e}")
            
            print(f"[CreateReel] ✅ Reel created successfully!")
            
            return CreateReelResponse(
                success=True,
                storage_url=storage_url,
                local_path=None  # ✅ No local path - only storage URL
            )
            
        except Exception as e:
            print(f"[CreateReel] ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return CreateReelResponse(
                success=False,
                error=str(e)
            )
