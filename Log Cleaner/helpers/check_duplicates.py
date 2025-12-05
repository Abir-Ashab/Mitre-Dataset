# python .\analyze_folder_sizes.py "Combined-Normal-Logs"

"""Script to CHECK duplicate and empty folders WITHOUT deleting."""
import os
import sys
from collections import defaultdict
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


def check_folder_contents(folder_id):
    """Check if a folder contains any files (not subfolders)."""
    service = authenticate()
    
    query = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        pageSize=10
    ).execute()
    
    files = results.get('files', [])
    return len(files), [f['name'] for f in files[:5]]  # Return count and first 5 filenames


def main():
    """Main function to CHECK duplicate and empty folders."""
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]
    else:
        folder_name = os.getenv("GDRIVE_CLEANED_LOGS_FOLDER", "Text_Logs")
    
    print(f"Checking folders in: {folder_name}")
    print("=" * 60)
    
    # Get the folder
    folder_id = get_folder_id(folder_name)
    print(f"Folder ID: {folder_id}\n")
    
    # Get all items in the main folder
    print("Fetching folder list...")
    items = get_files_in_folder_with_time(folder_id)
    print(f"Found {len(items)} items")
    
    # Filter to folders only
    folders_only = [f for f in items if f['mimeType'] == 'application/vnd.google-apps.folder']
    print(f"Found {len(folders_only)} folders\n")
    
    # Group folders by name
    name_groups = defaultdict(list)
    for folder in folders_only:
        name_groups[folder['name']].append(folder)
    
    # Check for duplicates
    print("=" * 60)
    print("DUPLICATE FOLDERS:")
    print("=" * 60)
    duplicate_count = 0
    for name, folder_list in name_groups.items():
        if len(folder_list) > 1:
            print(f"\n'{name}': {len(folder_list)} copies")
            folder_list.sort(key=lambda x: x['modifiedTime'], reverse=True)
            print(f"  Would keep: {folder_list[0]['id']} (modified: {folder_list[0]['modifiedTime']})")
            for dup in folder_list[1:]:
                print(f"  Would delete: {dup['id']} (modified: {dup['modifiedTime']})")
                duplicate_count += len(folder_list) - 1
    
    if duplicate_count == 0:
        print("No duplicate folders found.")
    else:
        print(f"\nTotal duplicate folders to delete: {duplicate_count}")
    
    # Check for empty folders
    print("\n" + "=" * 60)
    print("CHECKING FOR EMPTY FOLDERS:")
    print("=" * 60)
    print("(This may take a while...)\n")
    
    empty_folders = []
    deleted_ids = set()
    
    # Mark duplicates as deleted
    for name, folder_list in name_groups.items():
        if len(folder_list) > 1:
            for dup in folder_list[1:]:
                deleted_ids.add(dup['id'])
    
    for idx, folder in enumerate(folders_only, 1):
        if folder['id'] in deleted_ids:
            continue
            
        if idx % 50 == 0:
            print(f"Checked {idx}/{len(folders_only)} folders...")
        
        file_count, sample_files = check_folder_contents(folder['id'])
        
        if file_count == 0:
            empty_folders.append(folder)
            print(f"Empty: {folder['name']} (ID: {folder['id']})")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    print(f"Total folders: {len(folders_only)}")
    print(f"Duplicate folders to delete: {duplicate_count}")
    print(f"Empty folders to delete: {len(empty_folders)}")
    print(f"Total to delete: {duplicate_count + len(empty_folders)}")
    print(f"Remaining folders: {len(folders_only) - duplicate_count - len(empty_folders)}")


if __name__ == "__main__":
    main()
