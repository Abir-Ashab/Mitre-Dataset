"""Download folders with smallest JSON files from Google Drive."""
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


def get_folder_id(service, folder_name):
    """Get folder ID by name."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    else:
        raise ValueError(f"Folder '{folder_name}' not found")


def get_immediate_subfolders(service, folder_id):
    """Get immediate subfolders of a folder."""
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        pageSize=1000
    ).execute()
    return results.get('files', [])


def get_json_files_in_folder(service, folder_id):
    """Get all JSON files in a folder (non-recursive)."""
    query = f"'{folder_id}' in parents and name contains '.json' and trashed=false and mimeType!='application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, size)',
        pageSize=1000
    ).execute()
    return results.get('files', [])


def get_all_files_in_folder(service, folder_id):
    """Get all files in a folder recursively."""
    all_files = []
    folders_to_process = [folder_id]
    
    while folders_to_process:
        current_folder = folders_to_process.pop(0)
        
        query = f"'{current_folder}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, parents)',
            pageSize=1000
        ).execute()
        
        items = results.get('files', [])
        
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                folders_to_process.append(item['id'])
            else:
                all_files.append(item)
    
    return all_files


def calculate_folder_json_size(service, folder_id):
    """Calculate total size of JSON files in a folder."""
    json_files = get_json_files_in_folder(service, folder_id)
    total_size = sum(int(f.get('size', 0)) for f in json_files if f.get('size'))
    return total_size, len(json_files)


def download_file(service, file_id, local_path):
    """Download a file from Google Drive."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, 'wb') as f:
        f.write(fh.getvalue())


def download_folder_contents(service, folder_id, local_path, folder_name):
    """Download all files in a folder."""
    print(f"\nDownloading folder: {folder_name}")
    os.makedirs(local_path, exist_ok=True)
    
    all_files = get_all_files_in_folder(service, folder_id)
    
    # Create folder structure mapping
    folder_paths = {folder_id: local_path}
    
    # Get all folders to map their paths
    folders_to_check = [folder_id]
    while folders_to_check:
        current_folder = folders_to_check.pop(0)
        query = f"'{current_folder}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, parents)',
            pageSize=1000
        ).execute()
        
        subfolders = results.get('files', [])
        for subfolder in subfolders:
            parent_id = subfolder.get('parents', [None])[0]
            if parent_id in folder_paths:
                parent_path = folder_paths[parent_id]
                subfolder_path = os.path.join(parent_path, subfolder['name'])
                os.makedirs(subfolder_path, exist_ok=True)
                folder_paths[subfolder['id']] = subfolder_path
                folders_to_check.append(subfolder['id'])
    
    # Download all files
    downloaded = 0
    for file_item in all_files:
        parent_id = file_item.get('parents', [None])[0]
        if parent_id in folder_paths:
            parent_path = folder_paths[parent_id]
            file_path = os.path.join(parent_path, file_item['name'])
            
            if not os.path.exists(file_path):
                print(f"  Downloading: {file_item['name']}")
                download_file(service, file_item['id'], file_path)
                downloaded += 1
            else:
                print(f"  Skipping: {file_item['name']} (already exists)")
    
    print(f"  Downloaded {downloaded} file(s)")


def main():
    """Main function to download folders with smallest JSON files."""
    print("Starting selective download from Google Drive...")
    
    # Get configuration from environment
    source_folder_name = os.getenv("GDRIVE_LABELED_LOGS_FOLDER")
    total_logs = int(os.getenv("TOTAL_LOGS_TO_ANNOTATE", "10"))
    
    if not source_folder_name:
        print("Error: GDRIVE_LABELED_LOGS_FOLDER not set in .env")
        return
    
    print(f"Source folder: {source_folder_name}")
    print(f"Number of folders to download: {total_logs}")
    
    # Authenticate
    service = authenticate()
    
    # Get source folder ID
    try:
        source_folder_id = get_folder_id(service, source_folder_name)
        print(f"Source folder ID: {source_folder_id}")
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Get all immediate subfolders
    print("\nScanning subfolders...")
    subfolders = get_immediate_subfolders(service, source_folder_id)
    print(f"Found {len(subfolders)} subfolders")
    
    # Get list of existing folders to skip
    skip_folders = set()
    annotated_logs_path = os.path.join(os.getcwd(), "Annotated-Logs")
    pseudo_annotated_logs_path = os.path.join(os.getcwd(), "Pseudo-Annotated-Logs")
    
    for path in [annotated_logs_path, pseudo_annotated_logs_path]:
        if os.path.exists(path):
            existing_folders = {name for name in os.listdir(path) 
                               if os.path.isdir(os.path.join(path, name))}
            skip_folders.update(existing_folders)
    
    if skip_folders:
        print(f"\nFound {len(skip_folders)} existing folders to skip")
    
    # Filter out already downloaded folders
    subfolders_to_process = [f for f in subfolders if f['name'] not in skip_folders]
    print(f"Remaining folders to process: {len(subfolders_to_process)}")
    
    if not subfolders_to_process:
        print("\nNo new folders to download!")
        return
    
    # Calculate JSON file sizes for each folder
    print("\nCalculating JSON file sizes for each folder...")
    folder_sizes = []
    
    for i, folder in enumerate(subfolders_to_process, 1):
        print(f"  Analyzing {i}/{len(subfolders_to_process)}: {folder['name']}", end='')
        size, count = calculate_folder_json_size(service, folder['id'])
        folder_sizes.append({
            'id': folder['id'],
            'name': folder['name'],
            'size': size,
            'json_count': count
        })
        print(f" - {count} JSON file(s), {size:,} bytes")
    
    # Sort by size (smallest first)
    folder_sizes.sort(key=lambda x: x['size'])
    
    # Select top N folders
    folders_to_download = folder_sizes[:total_logs]
    
    print(f"\n{'='*60}")
    print(f"Selected {len(folders_to_download)} folder(s) with smallest JSON files:")
    print(f"{'='*60}")
    for i, folder in enumerate(folders_to_download, 1):
        print(f"{i}. {folder['name']}: {folder['json_count']} JSON file(s), {folder['size']:,} bytes")
    
    # Create local base directory
    local_base_path = "normal-logs"
    os.makedirs(local_base_path, exist_ok=True)
    
    # Download selected folders
    print(f"\n{'='*60}")
    print("Starting download...")
    print(f"{'='*60}")
    
    for i, folder in enumerate(folders_to_download, 1):
        print(f"\n[{i}/{len(folders_to_download)}]", end=' ')
        folder_local_path = os.path.join(local_base_path, folder['name'])
        download_folder_contents(service, folder['id'], folder_local_path, folder['name'])
    
    print(f"\n{'='*60}")
    print(f"Download complete! Files stored in: {local_base_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
