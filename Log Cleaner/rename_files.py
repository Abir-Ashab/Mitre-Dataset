"""Script to rename files inside folders following the naming convention."""
import os
import re
from dotenv import load_dotenv
from gdrive_helper import authenticate, get_folder_id

load_dotenv()


def rename_file(file_id, new_name):
    """Rename a file in Google Drive."""
    service = authenticate()
    
    file_metadata = {'name': new_name}
    updated_file = service.files().update(
        fileId=file_id,
        body=file_metadata,
        fields='id, name'
    ).execute()
    
    return updated_file


def get_all_folders(parent_folder_id):
    """Get all folders from Google Drive sorted by creation time."""
    service = authenticate()
    
    all_folders = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name, createdTime), nextPageToken',
            orderBy='createdTime asc',
            pageToken=page_token
        ).execute()
        
        all_folders.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    return all_folders


def get_files_in_folder(folder_id):
    """Get all files in a folder."""
    service = authenticate()
    
    files = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name), nextPageToken',
            pageToken=page_token
        ).execute()
        
        files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    return files


def rename_files_in_folder(folder_id, folder_name):
    """
    Rename files in folder to follow naming convention:
    - syslogs_{timestamp}.json
    - aw-watcher-web-chrome_{hostname}_logs_{timestamp}.json
    - screen_record_{timestamp}.avi/.mp4/.mkv
    - packet_capture_{timestamp}.pcap/.pcapng
    
    The timestamp is extracted from the folder name.
    """
    # Extract timestamp from folder name (assuming format: YYYYMMDD_HHMMSS)
    timestamp_match = re.search(r'(\d{8}_\d{6})', folder_name)
    if not timestamp_match:
        print(f"  ✗ Could not extract timestamp from folder name: {folder_name}")
        return 0
    
    timestamp = timestamp_match.group(1)
    print(f"  Using timestamp: {timestamp}")
    
    # Get all files in the folder
    files = get_files_in_folder(folder_id)
    
    if not files:
        print("  No files to rename in folder")
        return 0
    
    renamed_count = 0
    
    for file in files:
        old_name = file['name']
        new_name = None
        
        # Identify file type and create new name
        file_lower = old_name.lower()
        
        # System logs
        if ('syslog' in file_lower or 'system' in file_lower) and file_lower.endswith('.json'):
            new_name = f"syslogs_{timestamp}.json"
        
        # Browser logs - preserve hostname if present
        elif 'aw-watcher' in file_lower and file_lower.endswith('.json'):
            # Try to extract hostname from current name
            # Pattern: aw-watcher-web-chrome_{hostname}_logs_*
            match = re.search(r'aw-watcher-web-chrome[_-]([^_]+)_logs', old_name, re.IGNORECASE)
            if match:
                hostname = match.group(1)
                new_name = f"aw-watcher-web-chrome_{hostname}_logs_{timestamp}.json"
            else:
                # If no hostname found, use generic name
                new_name = f"aw-watcher-web-chrome_logs_{timestamp}.json"
        
        # Screen recording
        elif file_lower.endswith(('.avi', '.mp4', '.mkv')):
            # Keep original extension
            ext = os.path.splitext(old_name)[1]
            new_name = f"screen_record_{timestamp}{ext}"
        
        # Network capture
        elif file_lower.endswith(('.pcap', '.pcapng')):
            # Keep original extension
            ext = os.path.splitext(old_name)[1]
            new_name = f"packet_capture_{timestamp}{ext}"
        
        # If we determined a new name and it's different from old name
        if new_name and new_name != old_name:
            try:
                rename_file(file['id'], new_name)
                print(f"    ✓ Renamed: {old_name} → {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"    ✗ Failed to rename {old_name}: {e}")
        else:
            print(f"    • Keeping: {old_name}")
    
    return renamed_count


def main():
    """Main function to rename files in first 12 folders."""
    # Get the Attack-Logs folder ID
    attack_logs_folder = os.getenv('GDRIVE_FOLDER_NAME', 'Attack-Logs')
    print(f"Looking for folder: {attack_logs_folder}")
    
    try:
        folder_id = get_folder_id(attack_logs_folder)
        print(f"Found folder ID: {folder_id}")
    except Exception as e:
        print(f"Error finding folder: {e}")
        return
    
    # Get all folders sorted by creation time
    folders = get_all_folders(folder_id)
    print(f"\nFound {len(folders)} total folders")
    
    # Take first 24 folders
    folders_to_process = folders[:24]
    print(f"Processing first {len(folders_to_process)} folders\n")
    
    # Process each folder
    print("="*60)
    print("STARTING FILE RENAMING PROCESS")
    print("="*60)
    
    total_files_renamed = 0
    failed_folders = 0
    
    for i, folder in enumerate(folders_to_process, 1):
        try:
            print(f"\n[{i}/{len(folders_to_process)}] Folder: {folder['name']}")
            
            # Rename files inside the folder
            files_renamed = rename_files_in_folder(folder['id'], folder['name'])
            total_files_renamed += files_renamed
            print(f"  ✓ Renamed {files_renamed} file(s)")
        
        except Exception as e:
            print(f"  ✗ Error processing folder {folder['name']}: {e}")
            failed_folders += 1
    
    # Summary
    print("\n" + "="*60)
    print("RENAMING SUMMARY")
    print("="*60)
    print(f"Folders processed: {len(folders_to_process)}")
    print(f"Total files renamed: {total_files_renamed}")
    print(f"Failed folders: {failed_folders}")
    print("="*60)


if __name__ == "__main__":
    main()
