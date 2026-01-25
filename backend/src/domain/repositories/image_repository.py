"""
Image Repository Interface
Defines contract for image search and download services
"""
from abc import ABC, abstractmethod
from typing import Optional


class IImageRepository(ABC):
    """Interface for image search and download services (e.g., Pexels)"""
    
    @abstractmethod
    async def search_image(self, query: str) -> Optional[str]:
        """
        Search for image URL matching query
        
        Args:
            query: Search query
            
        Returns:
            Image URL or None if not found
        """
        pass
    
    @abstractmethod
    async def download_image(self, url: str, output_path: str) -> str:
        """
        Download image from URL to local path
        
        Args:
            url: Image URL
            output_path: Local path to save image
            
        Returns:
            Path to downloaded image
        """
        pass
