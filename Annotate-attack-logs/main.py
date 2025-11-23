"""Download folders and files from Google Drive."""
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive']


def authenticate():
    """Authenticate with Google Drive API."""
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
    
    return build('drive', 'v3', credentials=creds)


def get_folder_id(service, folder_name, parent_id=None):
    """Get folder ID by name."""
    if parent_id:
        query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    else:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    else:
        raise ValueError(f"Folder '{folder_name}' not found")


def get_all_items_in_folder(service, folder_id):
    """Get all items (files and folders) in a folder recursively."""
    all_items = []
    folders_to_process = [folder_id]
    
    while folders_to_process:
        current_folder = folders_to_process.pop(0)
        
        page_token = None
        while True:
            results = service.files().list(
                q=f"'{current_folder}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name, mimeType, parents), nextPageToken',
                pageToken=page_token
            ).execute()
            
            items = results.get('files', [])
            all_items.extend(items)
            
            # Add subfolders to process
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folders_to_process.append(item['id'])
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
    
    return all_items


def download_file(service, file_id, local_path):
    """Download a file from Google Drive."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    with open(local_path, 'wb') as f:
        f.write(fh.getvalue())


def create_local_structure(service, items, base_folder_id, local_base_path):
    """Create local directory structure and download files."""
    # Create a mapping of folder ID to local path
    folder_paths = {base_folder_id: local_base_path}
    
    # First pass: create all directories
    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            parent_id = item.get('parents', [None])[0]
            if parent_id in folder_paths:
                parent_path = folder_paths[parent_id]
                folder_path = os.path.join(parent_path, item['name'])
                os.makedirs(folder_path, exist_ok=True)
                folder_paths[item['id']] = folder_path
    
    # Second pass: download files
    for item in items:
        if item['mimeType'] != 'application/vnd.google-apps.folder':
            parent_id = item.get('parents', [None])[0]
            if parent_id in folder_paths:
                parent_path = folder_paths[parent_id]
                file_path = os.path.join(parent_path, item['name'])
                print(f"Downloading: {item['name']}")
                download_file(service, item['id'], file_path)


def main():
    """Main function to download folders and files."""
    print("Starting download from Google Drive...")
    
    # Get source folder name from environment
    source_folder_name = os.getenv("GDRIVE_LABELED_LOGS_FOLDER")
    if not source_folder_name:
        print("Error: GDRIVE_LABELED_LOGS_FOLDER not set in .env")
        return
    
    print(f"Source folder: {source_folder_name}")
    
    # Authenticate and get service
    service = authenticate()
    
    # Get source folder ID
    try:
        source_folder_id = get_folder_id(service, source_folder_name)
        print(f"Source folder ID: {source_folder_id}")
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Create local base directory
    local_base_path = source_folder_name
    os.makedirs(local_base_path, exist_ok=True)
    
    # Get all items in the source folder
    print("Scanning folder structure...")
    all_items = get_all_items_in_folder(service, source_folder_id)
    print(f"Found {len(all_items)} items total")
    
    # Create local structure and download files
    create_local_structure(service, all_items, source_folder_id, local_base_path)
    
    print(f"\nDownload complete! Files stored in: {local_base_path}")


if __name__ == "__main__":
    main()
