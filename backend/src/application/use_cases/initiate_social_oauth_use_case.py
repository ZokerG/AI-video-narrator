"""
Initiate Social OAuth Use Case
Generates OAuth authorization URL for social platforms
"""
from dataclasses import dataclass
import uuid

from src.domain.repositories.social_auth_repository import ISocialAuthRepository


@dataclass
class InitiateSocialOAuthRequest:
    """Request to initiate OAuth"""
    platform: str  # facebook, instagram, tiktok
    user_id: int
    redirect_uri: str


@dataclass
class InitiateSocialOAuthResponse:
    """Response with authorization URL"""
    success: bool
    authorization_url: str = ""
    state: str = ""
    error: str = ""


class InitiateSocialOAuthUseCase:
    """
    Use Case: Initiate OAuth flow for social platform
    
    Generates state token and authorization URL
    """
    
    def __init__(self, social_auth_repository: ISocialAuthRepository):
        self.social_auth = social_auth_repository
    
    async def execute(self, request: InitiateSocialOAuthRequest) -> InitiateSocialOAuthResponse:
        """
        Generate OAuth authorization URL
        
        Args:
            request: OAuth initiation request
            
        Returns:
            Response with authorization URL and state
        """
        try:
            # Generate CSRF state token with user ID
            state = f"{request.user_id}:{uuid.uuid4().hex}"
            
            # Get authorization URL for platform
            auth_url = self.social_auth.get_authorization_url(
                platform=request.platform,
                redirect_uri=request.redirect_uri,
                state=state
            )
            
            print(f"[InitiateOAuth] Generated URL for {request.platform}")
            
            return InitiateSocialOAuthResponse(
                success=True,
                authorization_url=auth_url,
                state=state
            )
            
        except Exception as e:
            print(f"[InitiateOAuth] ❌ Error: {str(e)}")
            return InitiateSocialOAuthResponse(
                success=False,
                error=str(e)
            )
