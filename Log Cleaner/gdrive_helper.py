"""Google Drive helper functions for authentication and file operations."""
import os
import pickle
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive']
_service = None


def authenticate():
    """Authenticate with Google Drive API."""
    global _service
    if _service:
        return _service
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    _service = build('drive', 'v3', credentials=creds)
    return _service


def get_folder_id(folder_name, parent_id=None):
    """Get or create a folder in Google Drive."""
    service = authenticate()
    
    if parent_id:
        query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    else:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    else:
        return create_folder(folder_name, parent_id)


def create_folder(folder_name, parent_folder_id=None):
    """Create a folder in Google Drive."""
    service = authenticate()
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def get_processed_sessions(text_logs_folder_id):
    """Get list of already processed session names from Text_Logs folder."""
    service = authenticate()
    
    query = f"'{text_logs_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(name)'
    ).execute()
    
    folders = results.get('files', [])
    
    # Return folder names directly (they match session names)
    processed = set(folder['name'] for folder in folders)
    
    return processed


def get_session_folders(parent_folder_id, limit=5):
    """Get the oldest N session folders from Google Drive."""
    service = authenticate()
    
    query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query, 
        spaces='drive', 
        fields='files(id, name, createdTime)',
        orderBy='createdTime asc',  # Changed from 'desc' to 'asc' for oldest first
        pageSize=1000  # Get more to filter out processed ones
    ).execute()
    
    return results.get('files', [])


def get_files_in_folder(folder_id):
    """Get all files in a Google Drive folder."""
    service = authenticate()
    
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType)'
    ).execute()
    
    return results.get('files', [])


def download_file(file_id, file_path):
    """Download a file from Google Drive."""
    service = authenticate()
    
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    with open(file_path, 'wb') as f:
        f.write(fh.getvalue())
    
    return file_path


def upload_file_from_content(content, folder_id, file_name, mime_type='text/plain'):
    """Upload file content to Google Drive."""
    service = authenticate()
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(
        io.BytesIO(content.encode('utf-8')),
        mimetype=mime_type,
        resumable=True
    )
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return file.get('id')
