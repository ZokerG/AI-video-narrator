"""
Main FastAPI Application - Clean Architecture
Combines all routers with OpenAPI documentation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import all routers
from src.presentation.api.routes import auth, videos, analysis, voices, social, reels

# Ensure directories exist (all temp files go into src/temp)
os.makedirs("src/temp/uploads", exist_ok=True)
os.makedirs("src/temp/outputs", exist_ok=True)
os.makedirs("src/assets/music", exist_ok=True)

# OpenAPI Configuration
app = FastAPI(
    title="AI Video Narrator API",
    description="""
    🎬 **AI-powered video narration platform using Clean Architecture**
    
    ## Features
    * 🧠 **AI Video Analysis** - Gemini-powered narrative generation
    * 🗣️ **Text-to-Speech** - ElevenLabs voice synthesis
    * 🎥 **Video Processing** - Automated audio mixing with MoviePy
    * ☁️ **Cloud Storage** - MinIO/S3 integration
    * 🔐 **OAuth Support** - Google, Facebook, Instagram, TikTok
    * 📱 **Viral Shorts** - Generate Instagram Reels & TikTok content
    
    ## Architecture
    Built with **Clean Architecture** principles:
    - Domain Layer (entities, repositories)
    - Application Layer (use cases)
    - Infrastructure Layer (adapters)
    - Presentation Layer (API routes)
    
    ## Getting Started
    1. Register at `/auth/register`
    2. Login at `/auth/login` to get access token
    3. Use token in Authorization header: `Bearer <token>`
    4. Upload video to `/analyze` endpoint
    """,
    version="2.0.0",
    contact={
        "name": "Quinesis Team",
        "url": "https://github.com/ZokerG/AI-video-narrator",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and registration endpoints"
        },
        {
            "name": "videos",
            "description": "Video management (list, delete)"
        },
        {
            "name": "analysis",
            "description": "🎯 Main feature - AI video analysis and narration"
        },
        {
            "name": "voices",
            "description": "Voice selection and preview"
        },
        {
            "name": "social-auth",
            "description": "Social media OAuth (Facebook, Instagram, TikTok)"
        },
        {
            "name": "reels",
            "description": "Viral short video generation"
        },
        {
            "name": "audio",
            "description": "Background music management"
        }
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    from src.infrastructure.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

# Mount static directories (from src/temp)
app.mount("/outputs", StaticFiles(directory="src/temp/outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="src/temp/uploads"), name="uploads")

# Include all routers
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(analysis.router)
app.include_router(voices.router)
app.include_router(voices.audio_router)  # Audio endpoints
app.include_router(social.router)
app.include_router(reels.router)

# Health check
@app.get("/", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "AI Video Narrator",
        "version": "2.0.0",
        "architecture": "Clean Architecture",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Video Narrator API...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
