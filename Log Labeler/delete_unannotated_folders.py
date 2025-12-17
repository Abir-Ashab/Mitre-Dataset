"""Script to delete folders from Combined-Attack-Logs that are not present in Pseudo-Annotated-Logs."""
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path to import gdrive_helper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Log Cleaner'))
from gdrive_helper import authenticate, get_folder_id

load_dotenv()


def get_all_folders(parent_folder_id):
    """Get all folders from a Google Drive parent folder."""
    service = authenticate()
    
    all_folders = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
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
    """Main function to delete unannotated folders."""
    source_folder = os.getenv('GDRIVE_TEXT_LOGS_FOLDER', 'Combined-Attack-Logs')
    annotated_folder = os.getenv('GDRIVE_LABELED_LOGS_FOLDER', 'Pseudo-Annotated-Logs')
    
    print("="*70)
    print("DELETE UNANNOTATED ATTACK LOG FOLDERS")
    print("="*70)
    print(f"\nSource folder: {source_folder}")
    print(f"Annotated folder: {annotated_folder}")
    
    # Get folder IDs
    print(f"\nFetching folder IDs...")
    try:
        source_folder_id = get_folder_id(source_folder)
        print(f"  ✓ {source_folder}: {source_folder_id}")
    except Exception as e:
        print(f"  ✗ Error finding {source_folder}: {e}")
        return
    
    try:
        annotated_folder_id = get_folder_id(annotated_folder)
        print(f"  ✓ {annotated_folder}: {annotated_folder_id}")
    except Exception as e:
        print(f"  ✗ Error finding {annotated_folder}: {e}")
        return
    
    # Get all folders from both locations
    print(f"\nFetching folders from {source_folder}...")
    source_folders = get_all_folders(source_folder_id)
    print(f"  Found {len(source_folders)} folders")
    
    print(f"\nFetching folders from {annotated_folder}...")
    annotated_folders = get_all_folders(annotated_folder_id)
    print(f"  Found {len(annotated_folders)} folders")
    
    # Create set of annotated folder names
    annotated_names = {folder['name'] for folder in annotated_folders}
    
    # Find folders to delete (in source but not in annotated)
    folders_to_delete = [
        folder for folder in source_folders 
        if folder['name'] not in annotated_names
    ]
    
    if not folders_to_delete:
        print("\n✓ All folders in source are annotated. Nothing to delete.")
        return
    
    # Show folders to be deleted
    print("\n" + "="*70)
    print(f"FOLDERS TO BE DELETED: {len(folders_to_delete)}")
    print("="*70)
    for i, folder in enumerate(folders_to_delete, 1):
        print(f"{i}. {folder['name']}")
    
    # Confirmation prompt
    print("\n" + "="*70)
    print("⚠️  WARNING: This will permanently DELETE the folders listed above!")
    print("="*70)
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\nOperation cancelled.")
        return
    
    # Delete folders
    print("\n" + "="*70)
    print("DELETING FOLDERS")
    print("="*70)
    
    deleted_count = 0
    failed_count = 0
    
    for i, folder in enumerate(folders_to_delete, 1):
        try:
            print(f"[{i}/{len(folders_to_delete)}] Deleting: {folder['name']}", end=" ")
            delete_folder(folder['id'])
            print("✓")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Error: {e}")
            failed_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("DELETION SUMMARY")
    print("="*70)
    print(f"Successfully deleted: {deleted_count}")
    print(f"Failed: {failed_count}")
    print(f"Remaining folders in {source_folder}: {len(source_folders) - deleted_count}")
    print("="*70)


if __name__ == "__main__":
    main()
