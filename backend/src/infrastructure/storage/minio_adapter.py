"""
MinIO Storage Adapter - Implements IStorageRepository interface
Wraps MinIO for object storage operations
"""
from typing import Tuple
import os
from src.domain.repositories.service_repositories import IStorageRepository


class MinIOAdapter(IStorageRepository):
    """Adapter for MinIO object storage"""
    
    def __init__(self):
        """Initialize MinIO adapter"""
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = os.getenv("MINIO_SECRET_KEY")
        self.bucket_name = os.getenv("MINIO_BUCKET", "quinesis")
    
    async def upload_video(
        self,
        file_path: str,
        user_id: int,
        filename: str
    ) -> Tuple[str, str]:
        """
        Upload video to MinIO storage
        
        Args:
            file_path: Local file path
            user_id: User identifier
            filename: Destination filename
            
        Returns:
            Tuple of (storage_url, object_name)
        """
        # Import existing implementation
        from src.infrastructure.storage.minio_storage import upload_file  # ✅ Correct function name
        
        # Create object name with user folder structure
        object_name = f"users/{user_id}/videos/{filename}"
        
        # Delegate to existing implementation
        result = upload_file(
            file_path=file_path,
            object_name=object_name
        )
        
        # Result is a dict with 'url' key
        url = result.get('url') if isinstance(result, dict) else result
        
        return (url, object_name)
    
    async def delete_video(self, object_name: str) -> bool:
        """
        Delete video from MinIO storage
        
        Args:
            object_name: Object path in storage
            
        Returns:
            True if successful
        """
        # Import existing implementation
        from src.infrastructure.storage.minio_storage import delete_file  # ✅ Correct function name
        
        # Delegate to existing implementation
        return delete_file(object_name=object_name)
