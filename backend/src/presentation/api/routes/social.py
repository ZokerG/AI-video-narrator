"""
Social Router - OAuth and account management endpoints
Uses Clean Architecture with dependency injection
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from src.infrastructure.database import get_db_session, User, SocialAccount
from src.infrastructure.auth import get_current_user

from src.application.use_cases.initiate_social_oauth_use_case import (
    InitiateSocialOAuthUseCase,
    InitiateSocialOAuthRequest
)
from src.application.use_cases.handle_social_oauth_callback_use_case import (
    HandleSocialOAuthCallbackUseCase,
    HandleSocialOAuthCallbackRequest
)
from src.presentation.api.dependencies import (
    get_initiate_social_oauth_use_case,
    get_handle_social_oauth_callback_use_case
)

router = APIRouter(tags=["social-auth"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@router.get("/auth/{platform}/login")
async def social_login(
    platform: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    use_case: InitiateSocialOAuthUseCase = Depends(get_initiate_social_oauth_use_case)
):
    """
    Initiate OAuth flow for social platform
    
    Redirects user to platform authorization page
    """
    valid_platforms = ("facebook", "instagram", "tiktok")
    if platform not in valid_platforms:
        raise HTTPException(400, f"Invalid platform. Valid: {valid_platforms}")
    
    # Build redirect URI
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/auth/{platform}/callback"
    
    response = await use_case.execute(
        InitiateSocialOAuthRequest(
            platform=platform,
            user_id=current_user.id,
            redirect_uri=redirect_uri
        )
    )
    
    if not response.success:
        raise HTTPException(500, response.error)
    
    return RedirectResponse(response.authorization_url)


@router.get("/auth/{platform}/callback")
async def social_callback(
    platform: str,
    code: str,
    state: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    use_case: HandleSocialOAuthCallbackUseCase = Depends(get_handle_social_oauth_callback_use_case)
):
    """
    Handle OAuth callback from social platform
    
    Exchanges code for token and saves account
    """
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/auth/{platform}/callback"
    
    response = await use_case.execute(
        HandleSocialOAuthCallbackRequest(
            platform=platform,
            code=code,
            state=state,
            redirect_uri=redirect_uri
        ),
        session=session
    )
    
    if not response.success:
        # Redirect to frontend with error
        return RedirectResponse(f"{FRONTEND_URL}/settings/connections?error={response.error}")
    
    # Redirect to frontend with success
    return RedirectResponse(f"{FRONTEND_URL}/settings/connections?success=true&platform={platform}")


@router.get("/social/accounts")
async def get_social_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get all connected social accounts for current user"""
    
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
                "picture_url": acc.picture_url,
                "connected_at": acc.created_at.isoformat() if acc.created_at else None
            }
            for acc in accounts
        ]
    }


@router.delete("/social/accounts/{account_id}")
async def disconnect_social_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Disconnect a social account"""
    
    stmt = select(SocialAccount).where(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    )
    result = await session.execute(stmt)
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(404, "Account not found")
    
    account.is_active = False
    await session.commit()
    
    return {"message": "Account disconnected"}
