"""
Analyze Video Use Case - Core business workflow
Orchestrates video analysis, TTS generation, audio mixing, and storage
"""
from dataclasses import dataclass
from typing import Optional
from src.domain.entities.video_analysis import VideoAnalysis
from src.domain.repositories.service_repositories import (
    IAIRepository,
    ITTSRepository,
    IVideoRepository,
    IStorageRepository
)


@dataclass
class AnalyzeVideoRequest:
    """Request to analyze a video"""
    video_path: str
    user_id: int
    style: str = "viral"
    pace: str = "medium"
    voice_id: Optional[str] = None
    language: str = "es"
    original_volume: float = 0.0
    background_music_path: Optional[str] = None
    session: Optional[any] = None  # Database session for saving video record


@dataclass
class AnalyzeVideoResponse:
    """Response with analyzed video"""
    success: bool
    analysis: Optional[VideoAnalysis] = None
    final_video_path: Optional[str] = None
    storage_url: Optional[str] = None
    error: Optional[str] = None


class AnalyzeVideoUseCase:
    """
    Use Case: Analyze video and generate narrated version
    
    This orchestrates the entire workflow:
    1. Analyze video with AI (Gemini)
    2. Generate TTS audio for narrative segments
    3. Mix audio with video
    4. Upload final video to storage
    """
    
    def __init__(
        self,
        ai_repository: IAIRepository,
        tts_repository: ITTSRepository,
        video_repository: IVideoRepository,
        storage_repository: IStorageRepository
    ):
        self.ai = ai_repository
        self.tts = tts_repository
        self.video = video_repository
        self.storage = storage_repository
    
    async def execute(self, request: AnalyzeVideoRequest) -> AnalyzeVideoResponse:
        """
        Execute the video analysis workflow
        
        Args:
            request: Video analysis request
            
        Returns:
            AnalyzeVideoResponse with results
        """
        try:
            # Step 1: Analyze video with AI
            print(f"[UseCase] Step 1: Analyzing video with AI...")
            analysis = await self.ai.analyze_video(
                video_path=request.video_path,
                style=request.style,
                pace=request.pace,
                voice_id=request.voice_id or "default",
                language=request.language
            )
            
            if not analysis or not analysis.beats:
                return AnalyzeVideoResponse(
                    success=False,
                    error="AI analysis produced no beats"
                )
            
            # Step 2: Generate TTS audio for each beat
            print(f"[UseCase] Step 2: Generating TTS audio for {len(analysis.beats)} beats...")
            audio_segments = []
            
            for beat in analysis.beats:
                if beat.voiceover and beat.voiceover.script:
                    audio_path, duration = await self.tts.generate_audio(
                        text=beat.voiceover.script,  # ✅ Fixed: text instead of script
                        voice_id=request.voice_id or "default",
                        style=request.style
                    )
                    
                    audio_segments.append({
                        "path": audio_path,
                        "start_s": beat.start_s or 0.0,
                        "duration": duration,
                        "pause_after": beat.voiceover.pause_after_s or 0.0
                    })
            
            # Step 3: Mix audio with video
            print(f"[UseCase] Step 3: Mixing {len(audio_segments)} audio segments with video...")
            final_video_path = f"src/temp/outputs/final_{request.user_id}_{int(__import__('time').time())}.mp4"
            
            output_path = await self.video.mix_audio_with_video(
                video_path=request.video_path,
                audio_segments=audio_segments,
                output_path=final_video_path,
                original_volume=request.original_volume
            )
            
            # Step 4: Upload to storage
            print("[UseCase] Step 4: Uploading final video to storage...")
            import os
            filename = os.path.basename(output_path)  # ✅ Extract filename from path
            storage_url, object_name = await self.storage.upload_video(
                file_path=output_path,
                user_id=request.user_id,
                filename=filename
            )
            
            # Step 5: Save video to database
            print("[UseCase] Step 5: Saving video record to database...")
            if request.session:
                from src.infrastructure.database import Video
                from datetime import datetime
                
                video_record = Video(
                    user_id=request.user_id,
                    original_filename=os.path.basename(request.video_path),
                    storage_object_name=object_name,
                    storage_url=storage_url,
                    status='completed',
                    voice_config={"voice_id": request.voice_id, "style": request.style},
                    audio_config={"original_volume": request.original_volume},
                    completed_at=datetime.utcnow()
                )
                request.session.add(video_record)
                await request.session.flush()
                print(f"   ✅ Video saved to DB with ID: {video_record.id}")
            
            # Step 6: Cleanup temp files
            print("[UseCase] Step 6: Cleaning up temporary files...")
            try:
                # Remove uploaded video
                if os.path.exists(request.video_path):
                    os.remove(request.video_path)
                    print(f"   ✅ Removed: {request.video_path}")
                
                # Remove generated audio files
                for seg in audio_segments:
                    if os.path.exists(seg['path']):
                        os.remove(seg['path'])
                        print(f"   ✅ Removed: {seg['path']}")
                
                # Remove final video (now in storage)
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"   ✅ Removed: {output_path}")
                    
            except Exception as cleanup_error:
                print(f"   ⚠️ Cleanup warning: {cleanup_error}")
            
            print(f"[UseCase] ✅ Workflow complete! Video available at: {storage_url}")
            
            return AnalyzeVideoResponse(
                success=True,
                analysis=analysis,
                final_video_path=None,  # ✅ No local path - only storage URL
                storage_url=storage_url
            )
            
        except Exception as e:
            print(f"[UseCase] ❌ Error in workflow: {str(e)}")
            return AnalyzeVideoResponse(
                success=False,
                error=str(e)
            )
