from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import uvicorn
import os
from pathlib import Path
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
from core.database import SocialAccount
import httpx
import uuid
from typing import Optional
from core.storage import save_video_to_drive, get_user_videos, delete_video
from elevenlabs import ElevenLabs

load_dotenv()

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("assets/music", exist_ok=True)

app = FastAPI(title="Gemini Video Narrator API")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    from core.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for EC2 deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],  # Explicitly allow Authorization header
)

# Mount static directories
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    email: EmailStr
    credits: int
    plan: str
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
    
    # Create access token (sub must be string)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "credits": user.credits,
            "plan": user.plan,
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
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Check if active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Create access token (sub must be string)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "credits": user.credits,
            "plan": user.plan,
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
        "plan": getattr(current_user, "plan", "free"),
        "created_at": current_user.created_at.isoformat()
    }

# ============= Google OAuth =============

@app.get("/auth/google/login")
async def google_login():
    """Initiate Google OAuth flow"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = "http://localhost:8000/auth/google/callback"
    scope = "openid email profile https://www.googleapis.com/auth/drive.file"
    
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&access_type=offline"
    )
    return RedirectResponse(url)

@app.get("/auth/google/callback")
async def google_callback(code: str, session: AsyncSession = Depends(get_db_session)):
    """Handle Google OAuth callback"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "http://localhost:8000/auth/google/callback"
    
    # 1. Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://oauth2.googleapis.com/token", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        })
        
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get token from Google")
            
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        # 2. Get user info
        user_res = await client.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={
            "Authorization": f"Bearer {access_token}"
        })
        
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
            
        user_info = user_res.json()
        email = user_info.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")

        # 3. Find or Create User
        user = await get_user_by_email(email, session)
        
        if not user:
            # Create new user with random password
            import secrets
            import string
            random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
            password_hash = hash_password(random_password)
            
            user = await create_user(email, password_hash, session)
        
        # 3.5. Update/Create SocialAccount (Store Tokens)
        from sqlalchemy import select
        refresh_token = token_data.get("refresh_token")
        
        # Check if social account exists
        stmt = select(SocialAccount).where(
            SocialAccount.user_id == user.id,
            SocialAccount.platform == 'google'
        )
        result = await session.execute(stmt)
        social_account = result.scalar_one_or_none()
        
        if social_account:
            # Update tokens
            social_account.access_token = access_token
            if refresh_token: # Only provided on first consent or explicit request
                social_account.refresh_token = refresh_token
            # social_account.token_expires_at = ... (Optional: calculate from expires_in)
        else:
            # Create new social account
            social_account = SocialAccount(
                user_id=user.id,
                platform='google',
                platform_user_id=user_info.get('id'),
                username=email,
                picture_url=user_info.get('picture'),
                access_token=access_token,
                refresh_token=refresh_token
            )
            session.add(social_account)
        
        await session.commit()
        token = create_access_token(data={"sub": str(user.id)})
        
        # 5. Redirect to Frontend (with token)
        frontend_url = "http://localhost:3000/auth/callback"
        return RedirectResponse(f"{frontend_url}?token={token}")

# ============= Audio Assets Endpoints =============

@app.get("/audio/background-tracks")
async def get_background_tracks():
    """List available background music tracks"""
    music_dir = "assets/music"
    tracks = []
    
    if os.path.exists(music_dir):
        for f in os.listdir(music_dir):
            if f.endswith(('.mp3', '.wav', '.m4a')):
                tracks.append({
                    "id": f, # filename as id
                    "name": f.replace("_", " ").replace("-", " ").rsplit('.', 1)[0].title(),
                    "filename": f,
                    "url": f"/audio/assets/{f}"
                })
    
    return {"tracks": tracks}

# Mount assets directory
app.mount("/audio/assets", StaticFiles(directory="assets/music"), name="audio_assets")

# ============= Video Processing Endpoints =============

@app.get("/voices")
async def get_voices():
    """Get all available ElevenLabs voices"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return {"error": "ElevenLabs API key not configured"}
    
    try:
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

@app.post("/voices/preview")
async def generate_voice_preview(
    voice_id: str = Form(...),
    text: str = Form("Hello, this is a sample of my voice. Do you like how I sound?"),
    current_user: User = Depends(get_current_user)
):
    """Generate audio preview for a voice"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")
    
    try:
        import uuid
        
        client = ElevenLabs(api_key=api_key)

        # Generate audio
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2"
        )
        
        # Convert generator to bytes
        audio_bytes = b"".join(audio_generator)
        
        # Save to temp file
        os.makedirs("outputs/previews", exist_ok=True)
        preview_filename = f"outputs/previews/preview_{uuid.uuid4().hex[:8]}.mp3"
        
        with open(preview_filename, "wb") as f:
             f.write(audio_bytes)
        
        # Return file URL
        return {
            "status": "success",
            "audio_url": f"http://localhost:8000/{preview_filename}",
            "voice_id": voice_id
        }
        
    except Exception as e:
        print(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

VIDEO_COST = 20

@app.post("/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    style: str = Form("viral"),
    pace: str = Form("fast"),
    voice_id: str = Form(None),
    original_volume: int = Form(10),
    background_track: Optional[str] = Form(None),
    background_volume: int = Form(10),
    stability: int = Form(50),
    similarity_boost: int = Form(75),
    speed: int = Form(100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Full pipeline: Upload -> Analyze -> TTS -> Mix
    """
    start_time = time.time()

    # 0. Check Credits
    if current_user.credits < VIDEO_COST:
        raise HTTPException(
            status_code=403, 
            detail=f"Insufficient credits. {VIDEO_COST} credits required. Balance: {current_user.credits}"
        )

    # 1. Save video locally
    video_filename = f"uploads/{int(time.time())}_{video.filename}"
    with open(video_filename, "wb") as buffer:
        content = await video.read()
        buffer.write(content)
        
    print(f"[{time.strftime('%X')}] 💾 Video saved to: {video_filename}")

    # 2. Check Duration (Free Plan Limit)
    if getattr(current_user, "plan", "free") == "free":
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(video_filename)
            duration = clip.duration
            clip.close()
            
            if duration > 60:
                os.remove(video_filename)
                raise HTTPException(
                    status_code=400,
                    detail=f"Free plan limit exceeded. Video is {int(duration)}s (limit: 60s)."
                )
        except HTTPException:
            raise
        except Exception as e:
            print(f"⚠️ Error checking duration: {e}")

    # Deduct credits
    current_user.credits -= VIDEO_COST
    session.add(current_user)
    await session.commit()
        
    try:
        from core.gemini import analyze_video_content
        print(f"[{time.strftime('%X')}] 🚀 Processing started for user {current_user.email} (Credits: {current_user.credits})")
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
        
        # 3. Generate TTS for narrative segments (beat-by-beat)
        from core.tts import generate_audio_for_beat
        audio_map = []
        
        print(f"[{time.strftime('%X')}] 🗣️ Starting TTS Generation for {len(analysis.beats)} narrative segments...")
        print(f"[{time.strftime('%X')}] 🎤 Using voice: {final_voice_id}")
        
        # Check if we have full narrative script for reference
        if analysis.overall and analysis.overall.full_narrative_script:
            full_narrative = analysis.overall.full_narrative_script
            word_count = len(full_narrative.split())
            print(f"   📖 Full narrative: {word_count} words")
            print(f"   📝 Preview: '{full_narrative[:100]}...'")
        
        last_audio_end = 0.0  # Track for overlap prevention
        
        for i, beat in enumerate(analysis.beats):
            audio_filename = f"outputs/audio_{beat.id}_{int(time.time())}.mp3"
            if beat.voiceover and beat.voiceover.script:
                script = beat.voiceover.script
                pause = beat.voiceover.pause_after_s or 0.0
                print(f"   ├─ Beat {i+1}/{len(analysis.beats)}: '{script[:40]}...'")
                
                result = generate_audio_for_beat(
                    script,
                    audio_filename,
                    voice_id=final_voice_id,
                    style=style,
                    voice_settings=voice_settings
                )
                if result:
                    path, duration = result
                    
                    # Prevent audio overlap
                    ideal_start = beat.start_s if beat.start_s is not None else 0.0
                    actual_start = max(ideal_start, last_audio_end)
                    
                    if actual_start > ideal_start:
                        delay = actual_start - ideal_start
                        print(f"   ⚠️ Beat {beat.id}: Audio delayed {delay:.2f}s to avoid overlap")
                    
                    audio_map.append({
                        "path": path,
                        "start_s": actual_start,
                        "duration": duration
                    })
                    
                    # Update tracker with audio duration + dramatic pause
                    last_audio_end = actual_start + duration + pause
                    
                    if pause > 0:
                        print(f"   🎭 Beat {beat.id}: +{pause}s dramatic pause after narration")
        
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
            original_volume_factor=volume_factor,
            background_track_path=f"assets/music/{background_track}" if background_track else None,
            background_volume_factor=background_volume / 100.0
        )
        
        print(f"[{time.strftime('%X')}] ✨ Processing finished! Output: {output_filename}")
        
        # Save to Google Drive
        video_record = await save_video_to_drive(
            user=current_user,
            video_path=output_filename,
            session=session,
            metadata={
                "original_filename": video.filename,
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
                },
                "background_audio": {
                    "track": background_track,
                    "volume": background_volume
                } if background_track else None
            }
        )
        await session.commit()
        
        
        # DEBUG: Inspect serialization
        analysis_dict = analysis.dict()
        print(f"📤 [DEBUG] Returning analysis with {len(analysis_dict.get('beats', []))} beats")
        if analysis_dict.get('beats'):
            first_beat = analysis_dict['beats'][0]
            print(f"   First beat keys: {list(first_beat.keys())}")
            if 'voiceover' in first_beat:
                print(f"   First beat voiceover: {first_beat['voiceover']}")
            else:
                print(f"   ⚠️ No voiceover in serialized beat!")
        
        print(f"[{time.strftime('%X')}] 💾 Video saved to MinIO (ID: {video_record.id})")
        print(f"[{time.strftime('%X')}] ⏱️ Total time: {time.time() - start_time:.2f}s")
        
        return {
            "status": "completed",
            "analysis": analysis_dict,
            "output_video": output_filename,
            "storage_url": video_record.storage_url,
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
                "storage_url": video.storage_url,
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

# ============= Social Media Authentication Endpoints =============

@app.get("/auth/{platform}/login")
async def social_login(platform: str, current_user: User = Depends(get_current_user)):
    """Convert platform to OAuth URL and redirect"""
    # Generate random state to prevent CSRF (and bind to user)
    state = f"{current_user.id}:{uuid.uuid4().hex}"
    
    redirect_uri = f"http://localhost:8000/auth/{platform}/callback"
    
    if platform == "facebook":
        client_id = os.getenv("FACEBOOK_CLIENT_ID")
        scope = "public_profile,pages_show_list,pages_read_engagement,pages_manage_posts"
        authorization_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope}"
        )
    
    elif platform == "instagram":
        # Usually handled via Facebook Login but with different permissions or IG Basic Display
        # We will assume Facebook Login for Pages flow here
        client_id = os.getenv("FACEBOOK_CLIENT_ID")
        scope = "instagram_basic,instagram_content_publish,pages_show_list"
        authorization_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope}"
        )
        
    elif platform == "tiktok":
        client_key = os.getenv("TIKTOK_CLIENT_KEY")
        scope = "user.info.basic,video.upload"
        authorization_url = (
            f"https://www.tiktok.com/v2/auth/authorize/?"
            f"client_key={client_key}&response_type=code&scope={scope}&redirect_uri={redirect_uri}&state={state}"
        )
        
    else:
        raise HTTPException(status_code=400, detail="Unsupported platform")
        
    return {"url": authorization_url}

@app.get("/auth/{platform}/callback")
async def social_callback(
    platform: str, 
    code: str, 
    state: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Handle OAuth callback"""
    # Extract user_id from state
    try:
        user_id = int(state.split(":")[0])
    except:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
        
    # Verify user exists
    from core.database import get_user_by_id
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    redirect_uri = f"http://localhost:8000/auth/{platform}/callback"
    access_token = ""
    platform_user_id = ""
    username = ""
    
    async with httpx.AsyncClient() as client:
        if platform == "facebook" or platform == "instagram":
            # Exchange code for token
            token_url = (
                f"https://graph.facebook.com/v18.0/oauth/access_token?"
                f"client_id={os.getenv('FACEBOOK_CLIENT_ID')}&"
                f"redirect_uri={redirect_uri}&"
                f"client_secret={os.getenv('FACEBOOK_CLIENT_SECRET')}&"
                f"code={code}"
            )
            resp = await client.get(token_url)
            data = resp.json()
            
            if "error" in data:
                raise HTTPException(status_code=400, detail=str(data["error"]))
                
            access_token = data["access_token"]
            
            # Get User Info
            me_url = f"https://graph.facebook.com/me?fields=id,name,picture&access_token={access_token}"
            me_resp = await client.get(me_url)
            me_data = me_resp.json()
            
            platform_user_id = me_data["id"]
            username = me_data.get("name", "Unknown")
            
        elif platform == "tiktok":
            # Exchange code for token
            token_url = "https://open.tiktokapis.com/v2/oauth/token/"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "client_key": os.getenv("TIKTOK_CLIENT_KEY"),
                "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
            resp = await client.post(token_url, headers=headers, data=data)
            token_data = resp.json()
            
            if "error" in token_data:
                 raise HTTPException(status_code=400, detail=str(token_data))
                 
            access_token = token_data.get("access_token")
            # For real implementation need to fetch user info
            platform_user_id = "tiktok_user" # Placeholder
            username = "TikTok User" # Placeholder

    # Save to DB
    from sqlalchemy import select
    # Check if account exists
    stmt = select(SocialAccount).where(
        SocialAccount.user_id == user_id,
        SocialAccount.platform == platform,
        SocialAccount.platform_user_id == platform_user_id
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.access_token = access_token
        existing.is_active = True
        # Update other fields
    else:
        new_account = SocialAccount(
            user_id=user_id,
            platform=platform,
            platform_user_id=platform_user_id,
            username=username,
            access_token=access_token,
            is_active=True
        )
        session.add(new_account)
        
    await session.commit()
    
    # Redirect back to frontend
    return {"status": "success", "message": f"{platform} connected successfully"}

@app.get("/social/accounts")
async def get_social_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """List connected social accounts"""
    from sqlalchemy import select
    stmt = select(SocialAccount).where(
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_active == True
    )
    result = await session.execute(stmt)
    accounts = result.scalars().all()
    
    return {
        "accounts": [
            {
                "id": acc.id,
                "platform": acc.platform,
                "username": acc.username,
                "created_at": acc.created_at.isoformat()
            }
            for acc in accounts
        ]
    }

# ============= Reels / Shorts Generator Endpoints =============

class ReelScriptRequest(BaseModel):
    topic: str
    style: str = "curious"

@app.post("/reels/generate-script")
async def generate_reel_script_endpoint(
    request: ReelScriptRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a script for a Reel based on a topic (Strict JSON)"""
    print(f"DEBUG: Received script generation request: {request}")
    
    try:
        from core.content_generator import generate_reels_script
        script_data = generate_reels_script(request.topic, request.style)
        return {"status": "success", "script": script_data}
    except Exception as e:
        print(f"Error generating script: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class ReelCreationRequest(BaseModel):
    script: dict
    voice_id: str
    bg_music: Optional[str] = None
    
@app.post("/reels/create")
async def create_reel_endpoint(
    request: ReelCreationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Create a Reel video from a generated script.
    1. Generate Audio (TTS)
    2. Download Images (Pexels)
    3. Assemble Video (MoviePy)
    4. Upload to S3
    """
    start_time = time.time()
    
    # Cost validation
    REEL_COST = 20
    if current_user.credits < REEL_COST:
        raise HTTPException(status_code=403, detail="Insufficient credits")

    try:
        # Prepare working directories
        job_id = f"reel_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        job_dir = Path(f"outputs/{job_id}")
        job_dir.mkdir(parents=True, exist_ok=True)
        
        script = request.script
        scenes = script.get('scenes', [])
        audio_map = []
        processed_scenes = []
        current_time_offset = 0.0
        
        # Imports
        from core.tts import generate_audio_for_beat
        from core.images import search_visual_for_scene, PexelsClient
        from core.video import create_reel_video
        
        pexels = PexelsClient()
        
        print(f"🎬 Starting Reel Job {job_id} for user {current_user.email}")
        
        # Step 1 & 2: Process Audio and Images concurrent-ish or sequential
        for i, scene in enumerate(scenes):
            # A. Audio
            audio_path = job_dir / f"audio_{i}.mp3"
            res_audio = generate_audio_for_beat(
                text=scene['narration'],
                output_path=str(audio_path),
                voice_id=request.voice_id
            )
            
            duration = scene.get('duration_estimate', 3.0)
            if res_audio:
                duration = res_audio[1]
                audio_map.append({
                     'path': str(audio_path),
                     'start_s': current_time_offset,
                     'duration': duration
                })
            
            # B. Images
            img_path = job_dir / f"image_{i}.jpg"
            query = scene.get('visual_query')
            if query:
                url = await search_visual_for_scene(query)
                if url:
                    await pexels.download_image(url, str(img_path))
                    scene['image_path'] = str(img_path)
                else:
                    scene['image_path'] = None
            
            scene['duration_estimate'] = duration
            processed_scenes.append(scene)
            current_time_offset += duration
            
        # Step 3: Assemble
        final_filename = f"final_{job_id}.mp4"
        final_path = job_dir / final_filename
        
        # BG Music
        bg_track_path = None
        if request.bg_music:
             bg_track_path = f"assets/music/{request.bg_music}"
             
        create_reel_video(
            scenes=processed_scenes,
            audio_map=audio_map,
            output_path=str(final_path),
            background_track=bg_track_path
        )
        
        # Step 4: Upload to Storage (S3/Drive)
        from core.storage import save_video_to_storage
        
        # Deduct credits
        current_user.credits -= REEL_COST
        session.add(current_user)
        
        video_record = await save_video_to_storage(
            user=current_user,
            video_path=str(final_path),
            session=session,
            metadata={
                "original_filename": f"Reel: {script.get('title')}.mp4",
                "voice_config": {"voice_id": request.voice_id},
                "audio_config": {"type": "reel_script", "bg_music": request.bg_music}
            }
        )
        
        await session.commit()
        
        print(f"✅ Reel Job {job_id} completed. Video ID: {video_record.id}")
        
        # Cleanup temporary files
        try:
            import shutil
            shutil.rmtree(job_dir)
            print(f"🧹 Cleaned up temporary directory: {job_dir}")
        except Exception as cleanup_error:
            print(f"⚠️ Warning: Failed to clean up {job_dir}: {cleanup_error}")
        
        return {
            "status": "completed",
            "video_id": video_record.id,
            "storage_url": video_record.storage_url,
            "credits_remaining": current_user.credits
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
