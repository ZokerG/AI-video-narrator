"""
Social Auth Repository Interface
Defines contract for social OAuth services
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class SocialUserProfile:
    """User profile from social platform"""
    platform_user_id: str
    username: str
    email: Optional[str] = None
    picture_url: Optional[str] = None


class ISocialAuthRepository(ABC):
    """Interface for social OAuth services"""
    
    @abstractmethod
    def get_authorization_url(
        self,
        platform: str,
        redirect_uri: str,
        state: str
    ) -> str:
        """
        Generate OAuth authorization URL
        
        Args:
            platform: Social platform (facebook, instagram, tiktok)
            redirect_uri: Callback URL
            state: CSRF state token
            
        Returns:
            Authorization URL
        """
        pass
    
    @abstractmethod
    async def exchange_code_for_token(
        self,
        platform: str,
        code: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """
        Exchange authorization code for access token
        
        Args:
            platform: Social platform
            code: Authorization code
            redirect_uri: Callback URL
            
        Returns:
            Dict with access_token, token_type, etc.
        """
        pass
    
    @abstractmethod
    async def get_user_profile(
        self,
        platform: str,
        access_token: str
    ) -> SocialUserProfile:
        """
        Get user profile from social platform
        
        Args:
            platform: Social platform
            access_token: OAuth access token
            
        Returns:
            SocialUserProfile with user data
        """
        pass
