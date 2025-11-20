"""Script to delete duplicate cleaned log files from Google Drive."""
import os
import sys
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from gdrive_helper import authenticate, get_folder_id

load_dotenv()


def get_files_in_folder_with_time(folder_id):
    """Get all files in a Google Drive folder with modified time."""
    service = authenticate()
    
    all_items = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name, mimeType, modifiedTime), nextPageToken',
            pageToken=page_token
        ).execute()
        
        all_items.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    return all_items


def delete_file(file_id):
    """Delete a file from Google Drive."""
    service = authenticate()
    service.files().delete(fileId=file_id).execute()


def get_all_files_recursive(folder_id):
    """Get all files recursively in a folder."""
    service = authenticate()
    
    all_files = []
    folders_to_process = [folder_id]
    
    while folders_to_process:
        current_folder = folders_to_process.pop(0)
        
        # Get files in current folder
        query = f"'{current_folder}' in parents and trashed=false"
        page_token = None
        while True:
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime), nextPageToken',
                pageToken=page_token
            ).execute()
            
            files = results.get('files', [])
            all_files.extend(files)
            
            # Add subfolders to process
            for file in files:
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    folders_to_process.append(file['id'])
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
    
    return all_files


def main():
    """Main function to delete duplicate folders."""
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]
    else:
        folder_name = os.getenv("GDRIVE_CLEANED_LOGS_FOLDER", "Text_Logs")
    
    print(f"Starting duplicate folder cleanup in folder: {folder_name}")
    
    # Get the folder
    folder_id = get_folder_id(folder_name)
    print(f"Folder ID: {folder_id}")
    
    # Get all items in the main folder
    items = get_files_in_folder_with_time(folder_id)
    print(f"Found {len(items)} items")
    
    # Filter to folders only
    folders_only = [f for f in items if f['mimeType'] == 'application/vnd.google-apps.folder']
    print(f"Found {len(folders_only)} folders")
    
    # Group folders by name
    name_groups = defaultdict(list)
    for folder in folders_only:
        name_groups[folder['name']].append(folder)
    
    total_deleted = 0
    
    # For each group with duplicates
    for name, folder_list in name_groups.items():
        if len(folder_list) > 1:
            print(f"Duplicate folders for '{name}': {len(folder_list)} copies")
            
            # Sort by modified time, keep the latest
            folder_list.sort(key=lambda x: x['modifiedTime'], reverse=True)
            to_keep = folder_list[0]
            to_delete = folder_list[1:]
            
            print(f"  Keeping: {to_keep['id']} (modified: {to_keep['modifiedTime']})")
            for dup in to_delete:
                print(f"  Deleting: {dup['id']} (modified: {dup['modifiedTime']})")
                delete_file(dup['id'])
                total_deleted += 1
    
    print(f"\nCleanup complete. Deleted {total_deleted} duplicate folders.")


if __name__ == "__main__":
    main()