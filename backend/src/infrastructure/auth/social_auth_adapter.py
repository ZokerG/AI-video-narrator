"""
Social Auth Adapter - Implements ISocialAuthRepository
Handles OAuth flows for Facebook, Instagram, TikTok
"""
from typing import Dict
import os
import httpx

from src.domain.repositories.social_auth_repository import (
    ISocialAuthRepository,
    SocialUserProfile
)


class SocialAuthAdapter(ISocialAuthRepository):
    """Adapter for social OAuth services"""
    
    def __init__(self):
        """Initialize with platform credentials from env"""
        self.facebook_client_id = os.getenv("FACEBOOK_CLIENT_ID")
        self.facebook_client_secret = os.getenv("FACEBOOK_CLIENT_SECRET")
        self.tiktok_client_key = os.getenv("TIKTOK_CLIENT_KEY")
        self.tiktok_client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    
    def get_authorization_url(
        self,
        platform: str,
        redirect_uri: str,
        state: str
    ) -> str:
        """Generate OAuth authorization URL for platform"""
        
        if platform == "facebook":
            scope = "public_profile,pages_show_list,pages_read_engagement,pages_manage_posts"
            return (
                f"https://www.facebook.com/v18.0/dialog/oauth?"
                f"client_id={self.facebook_client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"state={state}&"
                f"scope={scope}"
            )
        
        elif platform == "instagram":
            # Instagram uses Facebook OAuth with different scope
            scope = "instagram_basic,instagram_content_publish,pages_show_list"
            return (
                f"https://www.facebook.com/v18.0/dialog/oauth?"
                f"client_id={self.facebook_client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"state={state}&"
                f"scope={scope}"
            )
        
        elif platform == "tiktok":
            scope = "user.info.basic,video.upload"
            return (
                f"https://www.tiktok.com/v2/auth/authorize/?"
                f"client_key={self.tiktok_client_key}&"
                f"response_type=code&"
                f"scope={scope}&"
                f"redirect_uri={redirect_uri}&"
                f"state={state}"
            )
        
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    async def exchange_code_for_token(
        self,
        platform: str,
        code: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """Exchange auth code for access token"""
        
        async with httpx.AsyncClient() as client:
            if platform in ("facebook", "instagram"):
                token_url = (
                    f"https://graph.facebook.com/v18.0/oauth/access_token?"
                    f"client_id={self.facebook_client_id}&"
                    f"redirect_uri={redirect_uri}&"
                    f"client_secret={self.facebook_client_secret}&"
                    f"code={code}"
                )
                resp = await client.get(token_url)
                data = resp.json()
                
                if "error" in data:
                    raise Exception(f"OAuth error: {data['error']}")
                
                return data
            
            elif platform == "tiktok":
                token_url = "https://open.tiktokapis.com/v2/oauth/token/"
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                payload = {
                    "client_key": self.tiktok_client_key,
                    "client_secret": self.tiktok_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
                resp = await client.post(token_url, headers=headers, data=payload)
                data = resp.json()
                
                if "error" in data:
                    raise Exception(f"TikTok OAuth error: {data}")
                
                return data
            
            else:
                raise ValueError(f"Unsupported platform: {platform}")
    
    async def get_user_profile(
        self,
        platform: str,
        access_token: str
    ) -> SocialUserProfile:
        """Get user profile from platform"""
        
        async with httpx.AsyncClient() as client:
            if platform in ("facebook", "instagram"):
                me_url = f"https://graph.facebook.com/me?fields=id,name,picture&access_token={access_token}"
                resp = await client.get(me_url)
                data = resp.json()
                
                return SocialUserProfile(
                    platform_user_id=data.get("id", ""),
                    username=data.get("name", "Unknown"),
                    picture_url=data.get("picture", {}).get("data", {}).get("url")
                )
            
            elif platform == "tiktok":
                # TikTok requires different API call
                return SocialUserProfile(
                    platform_user_id="tiktok_user",
                    username="TikTok User"
                )
            
            else:
                raise ValueError(f"Unsupported platform: {platform}")
