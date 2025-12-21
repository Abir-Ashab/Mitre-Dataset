"""Script to rename 'New folder (*)' folders in Google Drive with proper timestamps."""
import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from gdrive_helper import authenticate, get_folder_id, get_files_in_folder, download_file

load_dotenv()

def get_all_folders(parent_folder_id):
    """Get all folders from Google Drive."""
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


def rename_folder(folder_id, new_name):
    """Rename a folder in Google Drive."""
    service = authenticate()
    
    file_metadata = {'name': new_name}
    updated_file = service.files().update(
        fileId=folder_id,
        body=file_metadata,
        fields='id, name'
    ).execute()
    
    return updated_file


def extract_timestamp_from_filename(filename):
    """Extract timestamp from filename.
    
    Expected formats:
    - 20251025_144900_browser.json
    - 20251025_144900_system.json
    - 20251025_144900_network.pcap
    - 2025-06-29 20-03-01.mkv
    """
    # Try to find pattern YYYYMMDD_HHMMSS
    match = re.search(r'(\d{8}_\d{6})', filename)
    if match:
        return match.group(1)
    
    # Try format: YYYY-MM-DD HH-MM-SS (video files)
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2})-(\d{2})-(\d{2})', filename)
    if match:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}_{match.group(4)}{match.group(5)}{match.group(6)}"
    
    # Try alternative format with dashes or other separators
    match = re.search(r'(\d{4})[-_](\d{2})[-_](\d{2})[-_\s](\d{2})[-_](\d{2})[-_](\d{2})', filename)
    if match:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}_{match.group(4)}{match.group(5)}{match.group(6)}"
    
    return None


def extract_timestamp_from_file_content(file_path):
    """Extract timestamp from file content if possible."""
    try:
        # Check if it's a JSON file
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Look for timestamp in various keys
                for key in ['timestamp', 'time', 'created_at', 'date']:
                    if key in data:
                        # Try to parse the timestamp
                        timestamp = data[key]
                        # Handle different formats
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            return dt.strftime('%Y%m%d_%H%M%S')
                        except:
                            pass
                
                # Check if it's a list of entries
                if isinstance(data, list) and len(data) > 0:
                    first_entry = data[0]
                    for key in ['timestamp', 'time', 'created_at', 'date']:
                        if key in first_entry:
                            timestamp = first_entry[key]
                            try:
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                return dt.strftime('%Y%m%d_%H%M%S')
                            except:
                                pass
    except Exception as e:
        print(f"Error reading file content: {e}")
    
    return None


def get_timestamp_from_file_metadata(file_item):
    """Extract timestamp from file's creation or modification time."""
    try:
        # Try to get createdTime first
        if 'createdTime' in file_item:
            timestamp_str = file_item['createdTime']
            # Parse ISO format: 2025-07-20T19:41:15.000Z
            dt = datetime.strptime(timestamp_str[:19], '%Y-%m-%dT%H:%M:%S')
            return dt.strftime('%Y%m%d_%H%M%S')
        
        # Fallback to modifiedTime
        if 'modifiedTime' in file_item:
            timestamp_str = file_item['modifiedTime']
            dt = datetime.strptime(timestamp_str[:19], '%Y-%m-%dT%H:%M:%S')
            return dt.strftime('%Y%m%d_%H%M%S')
    except Exception as e:
        print(f"  ✗ Error parsing file metadata: {e}")
    
    return None


def get_timestamp_for_folder(folder_id, folder_name):
    """Get timestamp for a folder by checking its files."""
    print(f"\n--- Checking folder: {folder_name} ---")
    
    # Get all files in the folder - need to request metadata fields
    service = authenticate()
    files = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name, createdTime, modifiedTime), nextPageToken',
            pageToken=page_token
        ).execute()
        
        files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    if not files:
        print(f"No files found in folder: {folder_name}")
        return None
    
    print(f"Found {len(files)} files in folder")
    
    # First, try to extract timestamp from filenames
    for file in files:
        filename = file['name']
        print(f"  Checking filename: {filename}")
        
        timestamp = extract_timestamp_from_filename(filename)
        if timestamp:
            print(f"  ✓ Found timestamp in filename: {timestamp}")
            return timestamp
    
    # If no timestamp in filename, try file metadata (for generic names like "video.mkv")
    print("No timestamp found in filenames, checking file metadata...")
    for file in files:
        filename = file['name']
        # Prioritize video files for metadata extraction
        if filename.endswith(('.mkv', '.mp4', '.avi')):
            print(f"  Checking metadata for video file: {filename}")
            timestamp = get_timestamp_from_file_metadata(file)
            if timestamp:
                print(f"  ✓ Found timestamp from file metadata: {timestamp}")
                return timestamp
    
    # Try all files metadata if video didn't work
    for file in files:
        timestamp = get_timestamp_from_file_metadata(file)
        if timestamp:
            print(f"  ✓ Found timestamp from file metadata: {timestamp}")
            return timestamp
    
    # If still no timestamp, try to download and check file content
    print("No timestamp found in metadata, checking file contents...")
    temp_dir = "temp_rename"
    os.makedirs(temp_dir, exist_ok=True)
    
    for file in files:
        filename = file['name']
        if filename.endswith('.json'):
            try:
                temp_file_path = os.path.join(temp_dir, filename)
                download_file(file['id'], temp_file_path)
                
                timestamp = extract_timestamp_from_file_content(temp_file_path)
                if timestamp:
                    print(f"  ✓ Found timestamp in file content: {timestamp}")
                    # Clean up
                    os.remove(temp_file_path)
                    return timestamp
                
                os.remove(temp_file_path)
            except Exception as e:
                print(f"  Error processing file {filename}: {e}")
    
    # Clean up temp directory
    try:
        os.rmdir(temp_dir)
    except:
        pass
    
    print(f"  ✗ Could not find timestamp for folder: {folder_name}")
    return None


def main():
    """Main function to rename folders."""
    # Get the Attack-Logs folder ID
    attack_logs_folder = os.getenv('GDRIVE_FOLDER_NAME', 'Attack-Logs')
    print(f"Looking for folder: {attack_logs_folder}")
    
    try:
        folder_id = get_folder_id(attack_logs_folder)
        print(f"Found folder ID: {folder_id}")
    except Exception as e:
        print(f"Error finding folder: {e}")
        return
    
    # Get all folders
    folders = get_all_folders(folder_id)
    print(f"\nFound {len(folders)} total folders")
    
    # Filter folders that match "New folder (*)" pattern or just "New folder"
    new_folders = [f for f in folders if re.match(r'^New folder( \(\d+\))?$', f['name'])]
    print(f"Found {len(new_folders)} folders matching 'New folder' pattern")
    
    if not new_folders:
        print("\nNo folders to rename!")
        return
    
    # Process each folder
    print("\n" + "="*60)
    print("STARTING FOLDER RENAMING PROCESS")
    print("="*60)
    
    renamed_count = 0
    failed_count = 0
    
    for folder in new_folders:
        try:
            timestamp = get_timestamp_for_folder(folder['id'], folder['name'])
            
            if timestamp:
                # Rename the folder
                new_name = timestamp
                print(f"\n→ Renaming '{folder['name']}' to '{new_name}'")
                
                result = rename_folder(folder['id'], new_name)
                print(f"✓ Successfully renamed to: {result['name']}")
                renamed_count += 1
            else:
                print(f"\n✗ Failed to find timestamp for: {folder['name']}")
                failed_count += 1
        
        except Exception as e:
            print(f"\n✗ Error processing folder {folder['name']}: {e}")
            failed_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("RENAMING SUMMARY")
    print("="*60)
    print(f"Total folders processed: {len(new_folders)}")
    print(f"Successfully renamed: {renamed_count}")
    print(f"Failed: {failed_count}")
    print("="*60)


if __name__ == "__main__":
    main()
