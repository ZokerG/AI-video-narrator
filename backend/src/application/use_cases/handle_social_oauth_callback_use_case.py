"""
Handle Social OAuth Callback Use Case
Processes OAuth callback, exchanges code for token, saves account
"""
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain.repositories.social_auth_repository import ISocialAuthRepository
from src.infrastructure.database import SocialAccount


@dataclass
class HandleSocialOAuthCallbackRequest:
    """Request to handle OAuth callback"""
    platform: str
    code: str
    state: str
    redirect_uri: str


@dataclass
class HandleSocialOAuthCallbackResponse:
    """Response after handling callback"""
    success: bool
    account_id: Optional[int] = None
    username: Optional[str] = None
    error: Optional[str] = None


class HandleSocialOAuthCallbackUseCase:
    """
    Use Case: Handle OAuth callback from social platform
    
    Workflow:
    1. Validate state (extract user_id)
    2. Exchange code for access token
    3. Get user profile
    4. Save/update SocialAccount in database
    """
    
    def __init__(self, social_auth_repository: ISocialAuthRepository):
        self.social_auth = social_auth_repository
    
    async def execute(
        self,
        request: HandleSocialOAuthCallbackRequest,
        session: AsyncSession
    ) -> HandleSocialOAuthCallbackResponse:
        """
        Process OAuth callback
        
        Args:
            request: Callback request with code and state
            session: Database session
            
        Returns:
            Response with account info
        """
        try:
            # Extract user_id from state
            try:
                user_id = int(request.state.split(":")[0])
            except:
                return HandleSocialOAuthCallbackResponse(
                    success=False,
                    error="Invalid state parameter"
                )
            
            print(f"[HandleCallback] Processing {request.platform} callback for user {user_id}")
            
            # Exchange code for token
            token_data = await self.social_auth.exchange_code_for_token(
                platform=request.platform,
                code=request.code,
                redirect_uri=request.redirect_uri
            )
            
            access_token = token_data.get("access_token")
            if not access_token:
                return HandleSocialOAuthCallbackResponse(
                    success=False,
                    error="Failed to get access token"
                )
            
            # Get user profile
            profile = await self.social_auth.get_user_profile(
                platform=request.platform,
                access_token=access_token
            )
            
            # Check if account exists
            stmt = select(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform == request.platform,
                SocialAccount.platform_user_id == profile.platform_user_id
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing account
                existing.access_token = access_token
                existing.username = profile.username
                existing.picture_url = profile.picture_url
                existing.is_active = True
                account_id = existing.id
            else:
                # Create new account
                new_account = SocialAccount(
                    user_id=user_id,
                    platform=request.platform,
                    platform_user_id=profile.platform_user_id,
                    username=profile.username,
                    picture_url=profile.picture_url,
                    access_token=access_token,
                    is_active=True
                )
                session.add(new_account)
                await session.flush()
                account_id = new_account.id
            
            await session.commit()
            
            print(f"[HandleCallback] ✅ Account saved: {profile.username}")
            
            return HandleSocialOAuthCallbackResponse(
                success=True,
                account_id=account_id,
                username=profile.username
            )
            
        except Exception as e:
            print(f"[HandleCallback] ❌ Error: {str(e)}")
            return HandleSocialOAuthCallbackResponse(
                success=False,
                error=str(e)
            )
