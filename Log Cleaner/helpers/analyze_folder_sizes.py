"""Script to analyze folder sizes in Google Drive."""
import os
import sys
from collections import defaultdict
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


def main():
    """Main function to analyze folder sizes."""
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]
    else:
        folder_name = os.getenv("GDRIVE_FOLDER_NAME", "Mitre-Dataset-Monitoring")
    
    print("=" * 60)
    print("Folder Size Analytics")
    print("=" * 60)
    print(f"Analyzing folder: {folder_name}\n")
    
    # Get the folder
    folder_id = get_folder_id(folder_name)
    print(f"Folder ID: {folder_id}\n")
    
    # Get all subfolders
    print("Fetching subfolder list...")
    folders = get_all_folders(folder_id)
    print(f"Found {len(folders)} folders\n")
    
    # Size categories
    size_categories = {
        'less_than_1gb': [],
        '1gb_to_1_5gb': [],
        '1_5gb_to_2gb': [],
        'greater_than_2gb': []
    }
    
    print("Analyzing folder sizes...")
    print("(This may take a while...)\n")
    
    for idx, folder in enumerate(folders, 1):
        if idx % 10 == 0:
            print(f"Analyzed {idx}/{len(folders)} folders...")
        
        total_size_bytes, total_size_gb, file_count = get_folder_size(folder['id'])
        
        folder_info = {
            'name': folder['name'],
            'id': folder['id'],
            'size_gb': total_size_gb,
            'size_bytes': total_size_bytes,
            'file_count': file_count
        }
        
        if total_size_gb < 1:
            size_categories['less_than_1gb'].append(folder_info)
        elif 1 <= total_size_gb < 1.5:
            size_categories['1gb_to_1_5gb'].append(folder_info)
        elif 1.5 <= total_size_gb < 2:
            size_categories['1_5gb_to_2gb'].append(folder_info)
        else:
            size_categories['greater_than_2gb'].append(folder_info)
    
    print(f"\nAnalyzed all {len(folders)} folders\n")
    
    # Print summary
    print("=" * 60)
    print("SIZE DISTRIBUTION SUMMARY")
    print("=" * 60)
    print(f"Less than 1 GB:      {len(size_categories['less_than_1gb']):4d} folders")
    print(f"1 GB to 1.5 GB:      {len(size_categories['1gb_to_1_5gb']):4d} folders")
    print(f"1.5 GB to 2 GB:      {len(size_categories['1_5gb_to_2gb']):4d} folders")
    print(f"Greater than 2 GB:   {len(size_categories['greater_than_2gb']):4d} folders")
    print(f"{'─' * 60}")
    print(f"Total:               {len(folders):4d} folders")
    
    # Print details for each category
    print("\n" + "=" * 60)
    print("DETAILED BREAKDOWN")
    print("=" * 60)
    
    for category_key, category_name in [
        ('less_than_1gb', 'LESS THAN 1 GB'),
        ('1gb_to_1_5gb', '1 GB TO 1.5 GB'),
        ('1_5gb_to_2gb', '1.5 GB TO 2 GB'),
        ('greater_than_2gb', 'GREATER THAN 2 GB')
    ]:
        folders_in_category = size_categories[category_key]
        print(f"\n{category_name}: {len(folders_in_category)} folders")
        print("─" * 60)
        
        if folders_in_category:
            # Sort by size descending
            folders_in_category.sort(key=lambda x: x['size_gb'], reverse=True)
            
            for folder_info in folders_in_category[:10]:  # Show top 10
                print(f"  {folder_info['name']}")
                print(f"    Size: {folder_info['size_gb']:.2f} GB ({folder_info['file_count']} files)")
            
            if len(folders_in_category) > 10:
                print(f"  ... and {len(folders_in_category) - 10} more folders")
            
            # Calculate total size for category
            total_category_size = sum(f['size_gb'] for f in folders_in_category)
            print(f"\n  Category Total: {total_category_size:.2f} GB")
    
    # Overall statistics
    print("\n" + "=" * 60)
    print("OVERALL STATISTICS")
    print("=" * 60)
    all_folders_info = []
    for category in size_categories.values():
        all_folders_info.extend(category)
    
    total_size_all = sum(f['size_gb'] for f in all_folders_info)
    total_files_all = sum(f['file_count'] for f in all_folders_info)
    
    print(f"Total size of all folders: {total_size_all:.2f} GB")
    print(f"Total number of files:     {total_files_all:,}")
    if all_folders_info:
        avg_size = total_size_all / len(all_folders_info)
        print(f"Average folder size:       {avg_size:.2f} GB")


if __name__ == "__main__":
    main()
