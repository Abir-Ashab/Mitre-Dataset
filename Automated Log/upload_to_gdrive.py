import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import io
import json

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Global service instance
_service = None

def authenticate():
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
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    _service = build('drive', 'v3', credentials=creds)
    return _service


def create_folder(folder_name, parent_folder_id=None):
    """Create a folder in Google Drive and return its ID."""
    service = authenticate()
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def upload_file_from_path(file_path, folder_id, file_name=None):
    """Upload a file from local path to Google Drive."""
    service = authenticate()
    if not file_name:
        file_name = os.path.basename(file_path)
    
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_name} to Google Drive")
    return file.get('id')


def upload_file_from_content(content, folder_id, file_name, mime_type='text/plain'):
    """Upload file content directly to Google Drive without saving locally."""
    service = authenticate()
    
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_name} to Google Drive")
    return file.get('id')


def upload_json_logs(logs_data, folder_id, file_name):
    """Upload JSON logs directly to Google Drive."""
    json_content = ""
    for log_entry in logs_data:
        json_content += json.dumps(log_entry) + "\n"
    
    return upload_file_from_content(json_content, folder_id, file_name, 'application/json')


def upload_folder(service, folder_path, parent_folder_id=None):
    """Upload entire folder structure (for backward compatibility)."""
    folder_name = os.path.basename(folder_path)
    folder_id = create_folder(folder_name, parent_folder_id)

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            upload_folder(service, item_path, folder_id)
        else:
            upload_file_from_path(item_path, folder_id)


def get_main_folder_id():
    """Get or create the main monitoring outputs folder."""
    service = authenticate()
    
    # Check if folder already exists
    results = service.files().list(
        q="name='Mitre-Dataset-Monitoring' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        return create_folder('Mitre-Dataset-Monitoring')


if __name__ == '__main__':
    service = authenticate()
    if os.path.exists('monitoring_outputs'):
        main_folder_id = get_main_folder_id()
        upload_folder(service, 'monitoring_outputs', main_folder_id)
