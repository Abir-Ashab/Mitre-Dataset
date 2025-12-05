"""Script to delete folders larger than 1.5 GB from Google Drive."""
import os
import sys
from dotenv import load_dotenv
from gdrive_helper import authenticate, get_folder_id

load_dotenv()


def get_folder_size(folder_id):
    """Calculate total size of all files in a Google Drive folder."""
    service = authenticate()
    
    query = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
    all_files = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(name, size), nextPageToken',
            pageToken=page_token
        ).execute()
        
        all_files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    total_size = 0
    for file in all_files:
        file_size = int(file.get('size', 0))
        total_size += file_size
    
    total_size_gb = total_size / (1024 * 1024 * 1024)
    return total_size, total_size_gb, len(all_files)


def get_all_folders(folder_id):
    """Get all subfolders in a Google Drive folder."""
    service = authenticate()
    
    query = f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
    all_folders = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name), nextPageToken',
            pageToken=page_token
        ).execute()
        
        all_folders.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    return all_folders


def delete_folder(folder_id):
    """Delete a folder from Google Drive."""
    service = authenticate()
    service.files().delete(fileId=folder_id).execute()


def main():
    """Main function to delete folders larger than 1.5 GB."""
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]
    else:
        folder_name = os.getenv("GDRIVE_FOLDER_NAME", "Mitre-Dataset-Monitoring")
    
    print("=" * 60)
    print("Delete Large Folders (> 1.5 GB)")
    print("=" * 60)
    print(f"Analyzing folder: {folder_name}\n")
    
    # Get the folder
    folder_id = get_folder_id(folder_name)
    print(f"Folder ID: {folder_id}\n")
    
    # Get all subfolders
    print("Fetching subfolder list...")
    folders = get_all_folders(folder_id)
    print(f"Found {len(folders)} folders\n")
    
    print("Analyzing folder sizes...")
    print("(This may take a while...)\n")
    
    folders_to_delete = []
    
    for idx, folder in enumerate(folders, 1):
        if idx % 10 == 0:
            print(f"Analyzed {idx}/{len(folders)} folders...")
        
        total_size_bytes, total_size_gb, file_count = get_folder_size(folder['id'])
        
        if total_size_gb > 1.5:
            folders_to_delete.append({
                'name': folder['name'],
                'id': folder['id'],
                'size_gb': total_size_gb,
                'file_count': file_count
            })
    
    print(f"\nAnalysis complete!\n")
    
    # Show folders to delete
    print("=" * 60)
    print(f"FOLDERS TO DELETE (> 1.5 GB): {len(folders_to_delete)} folders")
    print("=" * 60)
    
    if not folders_to_delete:
        print("No folders larger than 1.5 GB found.")
        return
    
    # Sort by size descending
    folders_to_delete.sort(key=lambda x: x['size_gb'], reverse=True)
    
    for folder_info in folders_to_delete:
        print(f"  {folder_info['name']}")
        print(f"    Size: {folder_info['size_gb']:.2f} GB ({folder_info['file_count']} files)")
        print(f"    ID: {folder_info['id']}")
    
    total_size_to_delete = sum(f['size_gb'] for f in folders_to_delete)
    print(f"\nTotal size to be freed: {total_size_to_delete:.2f} GB")
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    print("WARNING: This action cannot be undone!")
    print("=" * 60)
    response = input(f"\nDelete these {len(folders_to_delete)} folders? Type 'DELETE' to confirm: ").strip()
    
    if response == 'DELETE':
        print("\nDeleting folders...")
        deleted = 0
        failed = 0
        
        for folder_info in folders_to_delete:
            try:
                print(f"Deleting: {folder_info['name']} ({folder_info['size_gb']:.2f} GB)")
                delete_folder(folder_info['id'])
                deleted += 1
            except Exception as e:
                print(f"  Error: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Deletion complete!")
        print(f"  Deleted: {deleted} folders ({sum(f['size_gb'] for f in folders_to_delete[:deleted]):.2f} GB freed)")
        print(f"  Failed: {failed}")
        print("=" * 60)
    else:
        print("\nDeletion cancelled. No folders were deleted.")


if __name__ == "__main__":
    main()
