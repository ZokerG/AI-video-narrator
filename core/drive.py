"""
Google Drive integration for AI Video Narrator
Handles folder creation, file upload/download, and file management
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

# Scopes required for Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Get credentials file path
CREDENTIALS_FILE = os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE")
if not CREDENTIALS_FILE:
    raise ValueError("GOOGLE_DRIVE_CREDENTIALS_FILE not set in environment")

def get_drive_service():
    """Initialize and return Google Drive API service"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error initializing Drive service: {e}")
        raise

def create_folder(folder_name: str, parent_folder_id: Optional[str] = None) -> str:
    """
    Create a folder in Google Drive
    Returns the folder ID
    """
    service = get_drive_service()
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    try:
        folder = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        print(f"✅ Created folder '{folder_name}' with ID: {folder.get('id')}")
        return folder.get('id')
    except HttpError as error:
        print(f"Error creating folder: {error}")
        raise

def get_or_create_user_folder(user_email: str, root_folder_id: Optional[str] = None) -> Dict[str, str]:
    """
    Get or create user folder structure: root/user_email/outputs
    Returns dict with 'user_folder_id' and 'outputs_folder_id'
    """
    service = get_drive_service()
    
    # Step 1: Check if root "AI Video Narrator" folder exists
    if not root_folder_id:
        query = "name='AI Video Narrator' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        try:
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            if files:
                root_folder_id = files[0]['id']
                print(f"📁 Found existing root folder: {root_folder_id}")
            else:
                root_folder_id = create_folder("AI Video Narrator")
        except HttpError as error:
            print(f"Error searching for root folder: {error}")
            root_folder_id = create_folder("AI Video Narrator")
    
    # Step 2: Check if user folder exists
    query = f"name='{user_email}' and '{root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        if files:
            user_folder_id = files[0]['id']
            print(f"📁 Found existing user folder: {user_folder_id}")
        else:
            user_folder_id = create_folder(user_email, root_folder_id)
    except HttpError as error:
        print(f"Error searching for user folder: {error}")
        user_folder_id = create_folder(user_email, root_folder_id)
    
    # Step 3: Check if outputs folder exists
    query = f"name='outputs' and '{user_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        if files:
            outputs_folder_id = files[0]['id']
            print(f"📁 Found existing outputs folder: {outputs_folder_id}")
        else:
            outputs_folder_id = create_folder("outputs", user_folder_id)
    except HttpError as error:
        print(f"Error searching for outputs folder: {error}")
        outputs_folder_id = create_folder("outputs", user_folder_id)
    
    return {
        'user_folder_id': user_folder_id,
        'outputs_folder_id': outputs_folder_id
    }

def upload_file(file_path: str, folder_id: str, file_name: Optional[str] = None) -> Dict[str, str]:
    """
    Upload a file to Google Drive
    Returns dict with 'file_id' and 'web_view_link'
    """
    service = get_drive_service()
    
    if not file_name:
        file_name = os.path.basename(file_path)
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    # Detect mime type based on extension
    if file_path.endswith('.mp4'):
        mime_type = 'video/mp4'
    elif file_path.endswith('.mp3'):
        mime_type = 'audio/mpeg'
    else:
        mime_type = 'application/octet-stream'
    
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, size'
        ).execute()
        
        file_id = file.get('id')
        
        # Make file accessible with link
        service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        # Get direct download link
        download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        print(f"✅ Uploaded '{file_name}' to Drive (ID: {file_id})")
        
        return {
            'file_id': file_id,
            'web_view_link': file.get('webViewLink'),
            'download_link': download_link,
            'file_size': int(file.get('size', 0))
        }
    except HttpError as error:
        print(f"Error uploading file: {error}")
        raise

def delete_file(file_id: str) -> bool:
    """Delete a file from Google Drive"""
    service = get_drive_service()
    
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"🗑️ Deleted file from Drive (ID: {file_id})")
        return True
    except HttpError as error:
        print(f"Error deleting file: {error}")
        return False

def list_files_in_folder(folder_id: str) -> List[Dict]:
    """List all files in a folder"""
    service = get_drive_service()
    
    query = f"'{folder_id}' in parents and trashed=false"
    
    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, size, createdTime, webViewLink)',
            orderBy='createdTime desc'
        ).execute()
        
        return results.get('files', [])
    except HttpError as error:
        print(f"Error listing files: {error}")
        return []
