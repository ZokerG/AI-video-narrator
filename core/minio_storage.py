"""
MinIO Object Storage Module
S3-compatible storage for user videos and audio files
"""
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "ai-video-narrator")
MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

def get_s3_client():
    """
    Initialize and return S3 client configured for MinIO
    """
    return boto3.client(
        's3',
        endpoint_url=f"{'https' if MINIO_USE_SSL else 'http'}://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'  # MinIO doesn't care about region
    )

def create_bucket_if_not_exists():
    """
    Create the main bucket if it doesn't exist
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.head_bucket(Bucket=MINIO_BUCKET_NAME)
        print(f"✅ Bucket '{MINIO_BUCKET_NAME}' already exists")
    except ClientError:
        try:
            s3_client.create_bucket(Bucket=MINIO_BUCKET_NAME)
            print(f"✅ Created bucket '{MINIO_BUCKET_NAME}'")
        except Exception as e:
            print(f"❌ Error creating bucket: {e}")
            raise

def upload_file(file_path: str, object_name: str) -> Dict[str, str]:
    """
    Upload a file to MinIO
    
    Args:
        file_path: Local path to file
        object_name: S3 object name (e.g., 'users/1/videos/final_123.mp4')
    
    Returns:
        Dict with object_name, url, and file_size
    """
    s3_client = get_s3_client()
    
    # Determine content type
    if file_path.endswith('.mp4'):
        content_type = 'video/mp4'
    elif file_path.endswith('.mp3'):
        content_type = 'audio/mpeg'
    else:
        content_type = 'application/octet-stream'
    
    try:
        # Upload file
        file_size = os.path.getsize(file_path)
        
        s3_client.upload_file(
            file_path,
            MINIO_BUCKET_NAME,
            object_name,
            ExtraArgs={'ContentType': content_type}
        )
        
        # Generate presigned URL (valid for 7 days)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': MINIO_BUCKET_NAME,
                'Key': object_name
            },
            ExpiresIn=7 * 24 * 3600  # 7 days
        )
        
        print(f"✅ Uploaded '{object_name}' ({file_size} bytes)")
        
        return {
            'object_name': object_name,
            'url': presigned_url,
            'file_size': file_size
        }
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        raise

def delete_file(object_name: str) -> bool:
    """
    Delete a file from MinIO
    
    Args:
        object_name: S3 object name to delete
    
    Returns:
        True if successful, False otherwise
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.delete_object(Bucket=MINIO_BUCKET_NAME, Key=object_name)
        print(f"🗑️ Deleted '{object_name}'")
        return True
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        return False

def list_user_files(user_prefix: str):
    """
    List all files for a user
    
    Args:
        user_prefix: User folder prefix (e.g., 'users/1/')
    
    Returns:
        List of objects
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=MINIO_BUCKET_NAME,
            Prefix=user_prefix
        )
        
        return response.get('Contents', [])
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return []

def get_presigned_url(object_name: str, expiration: int = 7 * 24 * 3600) -> str:
    """
    Generate a presigned URL for an object
    
    Args:
        object_name: S3 object name
        expiration: URL expiration in seconds (default: 7 days)
    
    Returns:
        Presigned URL
    """
    s3_client = get_s3_client()
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': MINIO_BUCKET_NAME,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"❌ Error generating presigned URL: {e}")
        raise
