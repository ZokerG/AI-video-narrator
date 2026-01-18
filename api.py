from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import uvicorn
import os
import time
from dotenv import load_dotenv

# Import auth modules
from core.database import get_db_session, get_user_by_email, create_user, User
from core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from core.storage import save_video_to_drive, get_user_videos, delete_video

load_dotenv()

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app = FastAPI(title="Gemini Video Narrator API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads") # Optional if we want to view original

# Pydantic schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    credits: int
    created_at: str

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "Gemini Video Narrator"}

# ============= Authentication Endpoints =============

@app.post("/auth/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(request.email, session)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create user
    user = await create_user(request.email, password_hash, session)
    await session.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "credits": user.credits,
            "created_at": user.created_at.isoformat()
        }
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Login with email and password"""
    # Get user
    user = await get_user_by_email(request.email, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "credits": user.credits,
            "created_at": user.created_at.isoformat()
        }
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "credits": current_user.credits,
        "created_at": current_user.created_at.isoformat()
    }

# ============= Video Processing Endpoints =============

@app.get("/voices")
async def list_voices():
    """List available ElevenLabs voices"""
    try:
        from elevenlabs import ElevenLabs
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            return {"error": "ELEVENLABS_API_KEY not configured"}
        
        client = ElevenLabs(api_key=api_key)
        voices = client.voices.get_all()
        
        return {
            "voices": [
                {
                    "id": voice.voice_id,
                    "name": voice.name,
                    "description": getattr(voice, 'description', ''),
                    "labels": getattr(voice, 'labels', {}),
                }
                for voice in voices.voices
            ]
        }
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_video(
    file: UploadFile = File(...),
    keep_audio: bool = Form(True),  # Deprecated, use original_volume instead
    style: str = Form("viral"),
    pace: str = Form("fast"),
    voice_id: str = Form(None),
    stability: int = Form(50),
    similarity_boost: int = Form(70),
    speed: int = Form(100),
    original_volume: int = Form(30),  # 0-100 percentage
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    start_time = time.time()
    print(f"[{time.strftime('%X')}] 📥 New request: {file.filename} | Style: {style} | Pace: {pace}")
    print(f"[{time.strftime('%X')}] 🎙️ Voice Config: stability={stability}%, similarity={similarity_boost}%, speed={speed/100}x")
    print(f"[{time.strftime('%X')}] 🔊 Original Audio Volume: {original_volume}%")
    
    # 1. Save uploaded file
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    video_filename = f"uploads/{int(time.time())}_{file.filename}"
    with open(video_filename, "wb") as buffer:
        buffer.write(await file.read())
    
    print(f"[{time.strftime('%X')}] 💾 Video saved to: {video_filename}")
        
    try:
        # 2. Analyze with Gemini
        from core.gemini import analyze_video_content
        print(f"[{time.strftime('%X')}] 🧠 Starting Gemini Analysis...")
        analysis = analyze_video_content(video_filename, style=style, pace=pace)
        print(f"[{time.strftime('%X')}] ✅ Analysis complete. Beats found: {len(analysis.beats)}")
        
        # 3. Generate TTS with custom voice settings
        from core.tts import generate_audio_for_beat
        audio_map = []
        
        # Use voice_id from form or fallback to environment
        final_voice_id = voice_id if voice_id else os.environ.get("ELEVENLABS_VOICE_ID")
        
        # Create voice settings dict
        voice_settings = {
            "stability": stability / 100.0,  # Convert 0-100 to 0.0-1.0
            "similarity_boost": similarity_boost / 100.0,
            "speed": speed / 100.0  # Convert 70-120 to 0.7-1.2
        }
        
        print(f"[{time.strftime('%X')}] 🗣️ Starting TTS Generation for {len(analysis.beats)} beats...")
        print(f"[{time.strftime('%X')}] 🎤 Using voice: {final_voice_id}")
        
        for i, beat in enumerate(analysis.beats):
            audio_filename = f"outputs/audio_{beat.id}_{int(time.time())}.mp3"
            if beat.voiceover and beat.voiceover.script:
                print(f"   ├─ Generating Beat {i+1}/{len(analysis.beats)}: '{beat.voiceover.script[:30]}...'")
                result = generate_audio_for_beat(
                    beat.voiceover.script, 
                    audio_filename, 
                    voice_id=final_voice_id, 
                    style=style,
                    voice_settings=voice_settings
                )
                if result:
                    path, duration = result
                    audio_map.append({
                        "path": path,
                        "start_s": beat.start_s if beat.start_s is not None else 0.0,
                        "duration": duration
                    })
        print(f"[{time.strftime('%X')}] ✅ TTS Generation complete.")
        
        # 4. Mix Video with volume control
        from core.video import mix_audio_with_video
        output_filename = f"outputs/final_{int(time.time())}.mp4"
        print(f"[{time.strftime('%X')}] 🎬 Mixing audio and video...")
        print(f"[{time.strftime('%X')}] 🔊 Original audio volume: {original_volume}%")
        
        # Convert original_volume (0-100) to keep_audio boolean and volume factor
        volume_factor = original_volume / 100.0
        mix_audio_with_video(
            video_filename, 
            audio_map, 
            output_filename, 
            keep_original_audio=(original_volume > 0),
            original_volume_factor=volume_factor
        )
        
        print(f"[{time.strftime('%X')}] ✨ Processing finished! Output: {output_filename}")
        
        # Save to Google Drive
        video_record = await save_video_to_drive(
            user=current_user,
            video_path=output_filename,
            session=session,
            metadata={
                "original_filename": file.filename,
                "voice_config": {
                    "voice_id": voice_id,
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "speed": speed
                },
                "audio_config": {
                    "style": style,
                    "pace": pace,
                    "original_volume": original_volume
                }
            }
        )
        await session.commit()
        
        print(f"[{time.strftime('%X')}] 💾 Video saved to Drive (ID: {video_record.id})")
        print(f"[{time.strftime('%X')}] ⏱️ Total time: {time.time() - start_time:.2f}s")
        
        return {
            "status": "completed",
            "analysis": analysis.dict(),
            "output_video": output_filename,
            "drive_link": video_record.drive_link,
            "video_id": video_record.id
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[{time.strftime('%X')}] ❌ ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}

# ============= Video Management Endpoints =============

@app.get("/videos/my-videos")
async def get_my_videos(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get all videos for the current user"""
    videos = await get_user_videos(current_user.id, session)
    
    return {
        "videos": [
            {
                "id": video.id,
                "original_filename": video.original_filename,
                "drive_link": video.drive_link,
                "file_size": video.file_size,
                "status": video.status,
                "created_at": video.created_at.isoformat(),
                "voice_config": video.voice_config,
                "audio_config": video.audio_config
            }
            for video in videos
        ]
    }

@app.delete("/videos/{video_id}")
async def delete_user_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a video (requires ownership)"""
    success = await delete_video(video_id, current_user.id, session)
    
    if not success:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")
    
    await session.commit()
    
    return {"message": "Video deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
