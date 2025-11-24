"""Upload local folders and files to Google Drive."""
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
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


def get_or_create_folder(service, folder_name, parent_id=None):
    """Get or create a folder in Google Drive."""
    if parent_id:
        query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    else:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    else:
        # Create the folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')


def upload_file(service, local_path, folder_id, filename):
    """Upload a file to Google Drive."""
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    with open(local_path, 'rb') as f:
        media = MediaIoBaseUpload(f, mimetype='application/octet-stream', resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return file.get('id')


def upload_directory(service, local_path, parent_folder_id, folder_mapping):
    """Recursively upload a directory structure to Google Drive."""
    for root, dirs, files in os.walk(local_path):
        # Get relative path from local base
        rel_path = os.path.relpath(root, local_path)
        if rel_path == '.':
            current_parent_id = parent_folder_id
        else:
            # Create intermediate folders
            path_parts = rel_path.split(os.sep)
            current_parent_id = parent_folder_id
            
            for part in path_parts:
                if part not in folder_mapping:
                    folder_id = get_or_create_folder(service, part, current_parent_id)
                    folder_mapping[part] = folder_id
                current_parent_id = folder_mapping[part]
        
        # Upload files in current directory
        for file in files:
            local_file_path = os.path.join(root, file)
            print(f"Uploading: {os.path.join(rel_path, file) if rel_path != '.' else file}")
            upload_file(service, local_file_path, current_parent_id, file)


def main():
    """Main function to upload local folders and files."""
    print("Starting upload to Google Drive...")
    
    # Get destination folder name from environment
    dest_folder_name = os.getenv("UPLOAD_GDRIVE_LABELED_LOGS_FOLDER")
    if not dest_folder_name:
        print("Error: UPLOAD_GDRIVE_LABELED_LOGS_FOLDER not set in .env")
        return
    
    # Get source folder name from environment
    source_folder_name = os.getenv("GDRIVE_LABELED_LOGS_FOLDER")
    if not source_folder_name:
        print("Error: GDRIVE_LABELED_LOGS_FOLDER not set in .env")
        return
    
    print(f"Source local folder: {source_folder_name}")
    print(f"Destination Drive folder: {dest_folder_name}")
    
    # Check if local source exists
    if not os.path.exists(source_folder_name):
        print(f"Error: Local folder '{source_folder_name}' does not exist")
        return
    
    # Authenticate and get service
    service = authenticate()
    
    # Get or create destination folder
    dest_folder_id = get_or_create_folder(service, dest_folder_name)
    print(f"Destination folder ID: {dest_folder_id}")
    
    # Upload directory structure
    folder_mapping = {}
    upload_directory(service, source_folder_name, dest_folder_id, folder_mapping)
    
    print(f"\nUpload complete! Files uploaded to: {dest_folder_name}")


if __name__ == "__main__":
    main()