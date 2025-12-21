"""Script to move CSV files from Google Drive folders to Attack-CSV-Logs."""
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


def create_folder(folder_name, parent_folder_id):
    """Create a folder in Google Drive."""
    service = authenticate()
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def get_or_create_folder(folder_name, parent_folder_id):
    """Get folder ID if exists, otherwise create it."""
    service = authenticate()
    
    # Check if folder exists
    query = f"name='{folder_name}' and '{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        return create_folder(folder_name, parent_folder_id)


def move_file(file_id, new_parent_id, old_parent_id):
    """Move a file to a new parent folder."""
    service = authenticate()
    
    # Remove old parent and add new parent
    service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        fields='id, parents'
    ).execute()


def move_csv_files_in_folder(source_folder_id, source_folder_name, dest_parent_folder_id):
    """Move all CSV files from source folder to destination folder structure."""
    print(f"\n→ Processing folder: {source_folder_name}")
    
    # Get all CSV files in source folder
    csv_files = get_csv_files_in_folder(source_folder_id)
    
    if not csv_files:
        print("  • No CSV files found")
        return 0
    
    print(f"  Found {len(csv_files)} CSV file(s)")
    
    # Create/get destination folder with same name as source
    dest_folder_id = get_or_create_folder(source_folder_name, dest_parent_folder_id)
    print(f"  Destination folder ID: {dest_folder_id}")
    
    moved_count = 0
    failed_count = 0
    
    for csv_file in csv_files:
        try:
            print(f"  Moving: {csv_file['name']}", end=" ")
            move_file(csv_file['id'], dest_folder_id, source_folder_id)
            print("✓")
            moved_count += 1
        except Exception as e:
            print(f"✗ Error: {e}")
            failed_count += 1
    
    return moved_count


def main():
    """Main function to move CSV files from all folders."""
    # Get the Attack-Logs folder ID (source)
    attack_logs_folder = os.getenv('GDRIVE_FOLDER_NAME', 'Attack-Logs')
    print(f"Looking for source folder: {attack_logs_folder}")
    
    try:
        source_folder_id = get_folder_id(attack_logs_folder)
        print(f"Found source folder ID: {source_folder_id}")
    except Exception as e:
        print(f"Error finding source folder: {e}")
        return
    
    # Get or create the Attack-CSV-Logs folder (destination)
    dest_folder_name = 'Attack-CSV-Logs'
    print(f"\nLooking for/creating destination folder: {dest_folder_name}")
    
    try:
        # Try to get existing folder first
        try:
            dest_folder_id = get_folder_id(dest_folder_name)
            print(f"Found existing destination folder ID: {dest_folder_id}")
        except:
            # Create if doesn't exist (at root level)
            print(f"Creating new destination folder: {dest_folder_name}")
            dest_folder_id = create_folder(dest_folder_name, 'root')
            print(f"Created destination folder ID: {dest_folder_id}")
    except Exception as e:
        print(f"Error with destination folder: {e}")
        return
    
    # Get all folders from source
    folders = get_all_folders(source_folder_id)
    print(f"\nFound {len(folders)} folders to process")
    
    # Confirmation prompt
    print("\n" + "="*60)
    print(f"📁 This will MOVE all CSV files from '{attack_logs_folder}'")
    print(f"   to '{dest_folder_name}' (preserving folder structure)")
    print("="*60)
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Operation cancelled.")
        return
    
    # Move CSV files from each folder
    print("\n" + "="*60)
    print("STARTING CSV MIGRATION")
    print("="*60)
    
    total_moved = 0
    processed_folders = 0
    
    for i, folder in enumerate(folders, 1):
        try:
            print(f"\n[{i}/{len(folders)}] {folder['name']}")
            moved = move_csv_files_in_folder(
                folder['id'], 
                folder['name'], 
                dest_folder_id
            )
            total_moved += moved
            processed_folders += 1
        except Exception as e:
            print(f"  ✗ Error processing folder: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Folders processed: {processed_folders}/{len(folders)}")
    print(f"Total CSV files moved: {total_moved}")
    print(f"Destination: {dest_folder_name}")
    print("="*60)


if __name__ == "__main__":
    main()