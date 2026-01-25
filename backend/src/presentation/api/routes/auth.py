"""
Auth Router - Authentication and user management endpoints
OAuth 2.0 with refresh tokens
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import httpx
import os

# Import from infrastructure
from src.infrastructure.database import get_db_session, get_user_by_email, get_user_by_id, create_user, User
from src.infrastructure.auth import (
    hash_password, 
    verify_password, 
    create_tokens, 
    verify_refresh_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access_token expires
    user: dict

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    credits: int
    plan: str
    created_at: str


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Register a new user - returns access and refresh tokens"""
    existing_user = await get_user_by_email(request.email, session)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = hash_password(request.password)
    user = await create_user(request.email, password_hash, session)
    await session.commit()
    
    # Create both tokens
    access_token, refresh_token, expires_in = create_tokens(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": user.id,
            "email": user.email,
            "credits": user.credits,
            "plan": user.plan,
            "created_at": user.created_at.isoformat()
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Login with email and password - returns access and refresh tokens"""
    user = await get_user_by_email(request.email, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Create both tokens
    access_token, refresh_token, expires_in = create_tokens(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": user.id,
            "email": user.email,
            "credits": user.credits,
            "plan": user.plan,
            "created_at": user.created_at.isoformat()
        }
    }


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Refresh access token using refresh token"""
    # Verify refresh token
    user_id = verify_refresh_token(request.refresh_token)
    
    if user_id is None:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired refresh token"
        )
    
    # Verify user still exists and is active
    user = await get_user_by_id(user_id, session)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401, 
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token, refresh_token, expires_in = create_tokens(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


@router.get("/me", response_model=UserResponse)
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


@router.get("/google/login")
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


@router.get("/google/callback")
async def google_callback(code: str, session: AsyncSession = Depends(get_db_session)):
    """Handle Google OAuth callback"""
    # TODO: Implement Google OAuth token exchange
    raise HTTPException(501, "Google OAuth implementation pending")
