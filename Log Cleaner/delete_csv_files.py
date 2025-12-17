"""Script to delete CSV files from Google Drive folders after JSON conversion."""
import os
from dotenv import load_dotenv
from gdrive_helper import authenticate, get_folder_id

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


def get_csv_files_in_folder(folder_id):
    """Get all CSV files in a folder."""
    service = authenticate()
    
    csv_files = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name, mimeType), nextPageToken',
            pageToken=page_token
        ).execute()
        
        files = results.get('files', [])
        # Filter only CSV files
        csv_files.extend([f for f in files if f['name'].lower().endswith('.csv')])
        
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    return csv_files


def delete_file(file_id):
    """Delete a file from Google Drive."""
    service = authenticate()
    service.files().delete(fileId=file_id).execute()


def delete_csv_files_in_folder(folder_id, folder_name):
    """Delete all CSV files in a specific folder."""
    print(f"\n→ Processing folder: {folder_name}")
    
    # Get all CSV files in folder
    csv_files = get_csv_files_in_folder(folder_id)
    
    if not csv_files:
        print("  • No CSV files found")
        return 0
    
    print(f"  Found {len(csv_files)} CSV file(s)")
    
    deleted_count = 0
    failed_count = 0
    
    for csv_file in csv_files:
        try:
            print(f"  Deleting: {csv_file['name']}", end=" ")
            delete_file(csv_file['id'])
            print("✓")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Error: {e}")
            failed_count += 1
    
    return deleted_count


def main():
    """Main function to delete CSV files from all folders."""
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
    print(f"\nFound {len(folders)} folders to process")
    
    # Confirmation prompt
    print("\n" + "="*60)
    print("⚠️  WARNING: This will DELETE all CSV files in all folders!")
    print("="*60)
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Operation cancelled.")
        return
    
    # Delete CSV files from each folder
    print("\n" + "="*60)
    print("STARTING CSV DELETION")
    print("="*60)
    
    total_deleted = 0
    processed_folders = 0
    
    for i, folder in enumerate(folders, 1):
        try:
            print(f"\n[{i}/{len(folders)}] {folder['name']}")
            deleted = delete_csv_files_in_folder(folder['id'], folder['name'])
            total_deleted += deleted
            processed_folders += 1
        except Exception as e:
            print(f"  ✗ Error processing folder: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("DELETION SUMMARY")
    print("="*60)
    print(f"Folders processed: {processed_folders}/{len(folders)}")
    print(f"Total CSV files deleted: {total_deleted}")
    print("="*60)


if __name__ == "__main__":
    main()
