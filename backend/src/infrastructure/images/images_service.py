import os
import httpx
import asyncio
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class PexelsClient:
    BASE_URL = "https://api.pexels.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            print("⚠️ Warning: PEXELS_API_KEY not found. Image search will fail.")
            
    async def search_images(self, query: str, orientation: str = "portrait", per_page: int = 1) -> List[Dict]:
        """
        Search for images on Pexels.
        orientation: 'landscape', 'portrait', or 'square'
        """
        if not self.api_key:
            return []
            
        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": per_page,
            "locale": "en-US" # Pexels search works best in English
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/search", headers=headers, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                photos = []
                for photo in data.get("photos", []):
                    # Prefer original or large2x for quality
                    src = photo.get("src", {})
                    image_url = src.get("original") or src.get("large2x") or src.get("large")
                    
                    if image_url:
                        photos.append({
                            "id": photo.get("id"),
                            "url": image_url,
                            "photographer": photo.get("photographer"),
                            "width": photo.get("width"),
                            "height": photo.get("height"),
                            "avg_color": photo.get("avg_color")
                        })
                return photos
                
            except Exception as e:
                print(f"❌ Error searching Pexels for '{query}': {e}")
                return []

    async def download_image(self, url: str, output_path: str) -> bool:
        """Download image from URL to local path"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, follow_redirects=True, timeout=30.0)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            except Exception as e:
                print(f"❌ Error downloading image {url}: {e}")
                return False

# Singleton or helper function
async def search_visual_for_scene(query: str) -> Optional[str]:
    """Helper to get a single image URL for a scene"""
    client = PexelsClient()
    results = await client.search_images(query, orientation="portrait", per_page=1)
    if results:
        return results[0]['url']
    return None
