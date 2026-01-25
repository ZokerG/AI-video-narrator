"""
Dependency Injection - FastAPI Dependencies
Provides instances of use cases with their required adapters
"""
from functools import lru_cache
import os

# Domain
from src.domain.repositories.service_repositories import (
    IAIRepository,
    ITTSRepository,
    IVideoRepository,
    IStorageRepository
)
from src.domain.repositories.image_repository import IImageRepository
from src.domain.repositories.social_auth_repository import ISocialAuthRepository

# Infrastructure
from src.infrastructure.ai.gemini_adapter import GeminiAdapter
from src.infrastructure.tts.elevenlabs_adapter import ElevenLabsAdapter
from src.infrastructure.video.moviepy_adapter import MoviePyAdapter
from src.infrastructure.storage.minio_adapter import MinIOAdapter
from src.infrastructure.images.pexels_adapter import PexelsAdapter
from src.infrastructure.auth.social_auth_adapter import SocialAuthAdapter

# Application
from src.application.use_cases.analyze_video_use_case import AnalyzeVideoUseCase
from src.application.use_cases.generate_reel_script_use_case import GenerateReelScriptUseCase
from src.application.use_cases.create_reel_use_case import CreateReelUseCase
from src.application.use_cases.initiate_social_oauth_use_case import InitiateSocialOAuthUseCase
from src.application.use_cases.handle_social_oauth_callback_use_case import HandleSocialOAuthCallbackUseCase


# ============= Repository Providers =============

@lru_cache()
def get_ai_repository() -> IAIRepository:
    """Provide AI repository (Gemini)"""
    api_key = os.getenv("GOOGLE_API_KEY")
    return GeminiAdapter(api_key=api_key)


@lru_cache()
def get_tts_repository() -> ITTSRepository:
    """Provide TTS repository (ElevenLabs)"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    return ElevenLabsAdapter(api_key=api_key)


@lru_cache()
def get_video_repository() -> IVideoRepository:
    """Provide video processing repository (MoviePy)"""
    return MoviePyAdapter()


@lru_cache()
def get_storage_repository() -> IStorageRepository:
    """Provide storage repository (MinIO)"""
    return MinIOAdapter()


@lru_cache()
def get_image_repository() -> IImageRepository:
    """Provide image repository (Pexels)"""
    return PexelsAdapter()


@lru_cache()
def get_social_auth_repository() -> ISocialAuthRepository:
    """Provide social auth repository"""
    return SocialAuthAdapter()


# ============= Use Case Providers =============

def get_analyze_video_use_case() -> AnalyzeVideoUseCase:
    """Provide AnalyzeVideoUseCase with all dependencies"""
    return AnalyzeVideoUseCase(
        ai_repository=get_ai_repository(),
        tts_repository=get_tts_repository(),
        video_repository=get_video_repository(),
        storage_repository=get_storage_repository()
    )


def get_generate_reel_script_use_case() -> GenerateReelScriptUseCase:
    """Provide GenerateReelScriptUseCase with dependencies"""
    return GenerateReelScriptUseCase(
        ai_repository=get_ai_repository()
    )


def get_create_reel_use_case() -> CreateReelUseCase:
    """Provide CreateReelUseCase with all dependencies"""
    return CreateReelUseCase(
        tts_repository=get_tts_repository(),
        image_repository=get_image_repository(),
        video_repository=get_video_repository(),
        storage_repository=get_storage_repository()
    )


def get_initiate_social_oauth_use_case() -> InitiateSocialOAuthUseCase:
    """Provide InitiateSocialOAuthUseCase"""
    return InitiateSocialOAuthUseCase(
        social_auth_repository=get_social_auth_repository()
    )


def get_handle_social_oauth_callback_use_case() -> HandleSocialOAuthCallbackUseCase:
    """Provide HandleSocialOAuthCallbackUseCase"""
    return HandleSocialOAuthCallbackUseCase(
        social_auth_repository=get_social_auth_repository()
    )
