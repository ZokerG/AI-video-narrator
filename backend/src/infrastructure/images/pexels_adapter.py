"""
Pexels Image Adapter - Implements IImageRepository
Wraps Pexels API for image search and download
"""
from typing import Optional
from src.domain.repositories.image_repository import IImageRepository


class PexelsAdapter(IImageRepository):
    """Adapter for Pexels image service"""
    
    def __init__(self):
        """Initialize Pexels adapter"""
        # Pexels client is initialized in core.images
        pass
    
    async def search_image(self, query: str) -> Optional[str]:
        """
        Search for image URL on Pexels
        
        Args:
            query: Search query
            
        Returns:
            Image URL or None
        """
        # Delegate to existing implementation
        from src.infrastructure.images.images_service import search_visual_for_scene
        
        url = await search_visual_for_scene(query)
        return url
    
    async def download_image(self, url: str, output_path: str) -> str:
        """
        Download image from URL
        
        Args:
            url: Image URL
            output_path: Local path to save
            
        Returns:
            Path to downloaded image
        """
        # Delegate to existing implementation
        from src.infrastructure.images.images_service import PexelsClient
        
        client = PexelsClient()
        await client.download_image(url, output_path)
        
        return output_path
