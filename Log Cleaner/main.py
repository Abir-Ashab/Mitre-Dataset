"""Main script for downloading, cleaning, and uploading logs."""
import os
import sys
import json
import shutil
from dotenv import load_dotenv
from gdrive_helper import (
    get_folder_id, get_session_folders, get_files_in_folder,
    download_file, upload_file_from_content, create_folder,
    get_processed_sessions
)
from log_parser import (
    parse_browser_logs, parse_system_logs, parse_pcap_logs,
    remove_duplicates, standardize_timestamps
)

load_dotenv()

TEMP_DOWNLOAD_DIR = "temp_downloads"


def get_env_or_fail(var):
    """Get environment variable or exit if not set."""
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value


def download_session_logs(session_folder):
    """Download all log files from a session folder (skip video files)."""
    print(f"\n=== Downloading logs from: {session_folder['name']} ===")
    
    session_dir = os.path.join(TEMP_DOWNLOAD_DIR, session_folder['name'])
    os.makedirs(session_dir, exist_ok=True)
    
    files = get_files_in_folder(session_folder['id'])
    
    downloaded_files = {'pcap': None, 'browser': None, 'system': None}
    
    for file in files:
        file_name = file['name']
        
        # Skip video files
        if file_name.endswith(('.avi', '.mp4', '.mkv')):
            print(f"Skipping video file: {file_name}")
            continue
        
        print(f"Downloading: {file_name}")
        file_path = os.path.join(session_dir, file_name)
        download_file(file['id'], file_path)
        
        # Categorize the file
        if file_name.endswith('.pcap'):
            downloaded_files['pcap'] = file_path
        elif 'aw-watcher' in file_name or 'browser' in file_name:
            downloaded_files['browser'] = file_path
        elif 'syslog' in file_name:
            downloaded_files['system'] = file_path
    
    return downloaded_files, session_dir


def merge_and_clean_logs(pcap_path, browser_path, sys_path):
    """Parse, merge, and clean all log files."""
    print("\n=== Starting Log Processing ===")
    
    all_events = []
    
    if pcap_path and os.path.exists(pcap_path):
        print(f"\nProcessing PCAP: {pcap_path}")
        all_events.extend(parse_pcap_logs(pcap_path))
    
    if browser_path and os.path.exists(browser_path):
        print(f"\nProcessing Browser Log: {browser_path}")
        all_events.extend(parse_browser_logs(browser_path))
    
    if sys_path and os.path.exists(sys_path):
        print(f"\nProcessing System Log: {sys_path}")
        all_events.extend(parse_system_logs(sys_path))
    
    print(f"\nTotal events before cleaning: {len(all_events)}")
    
    all_events = remove_duplicates(all_events)
    all_events = standardize_timestamps(all_events)
    all_events.sort(key=lambda x: x.get('timestamp') or '')
    
    print(f"Total events after cleaning: {len(all_events)}")
    
    return all_events


def upload_cleaned_logs(cleaned_events, session_name):
    """Upload text logs to Google Drive with original session timestamp."""
    print("\n=== Uploading to Google Drive ===")
    
    # Get or create the Text_Logs folder
    text_logs_folder_name = os.getenv("GDRIVE_CLEANED_LOGS_FOLDER", "Text_Logs")
    text_logs_parent_id = get_folder_id(text_logs_folder_name)
    print(f"Text Logs folder ID: {text_logs_parent_id}")
    
    # Create folder with original session name (no prefix)
    session_folder_id = create_folder(session_name, text_logs_parent_id)
    print(f"Created session folder: {session_name} (ID: {session_folder_id})")
    
    # Upload with original session timestamp in filename
    file_name = f"text_log_{session_name}.json"
    
    cleaned_json = json.dumps(cleaned_events, indent=2)
    upload_file_from_content(cleaned_json, session_folder_id, file_name, mime_type='application/json')
    
    print(f"Successfully uploaded: {file_name}")
    print(f"Total events uploaded: {len(cleaned_events)}")


def cleanup_temp_files(temp_dir):
    """Delete temporary downloaded files."""
    if os.path.exists(temp_dir):
        print(f"\n=== Cleaning up temporary files ===")
        shutil.rmtree(temp_dir)
        print(f"Deleted: {temp_dir}")


def main():
    """Main function to download, clean, and upload logs."""
    print("=" * 60)
    print("Log Cleaner & Uploader - Automated Processing")
    print("=" * 60)
    
    # Get configuration
    num_sessions = int(os.getenv("NUM_SESSIONS_TO_PROCESS", "5"))
    print(f"\nProcessing up to {num_sessions} unprocessed log sessions")
    
    # Get main folder
    main_folder_name = get_env_or_fail("GDRIVE_FOLDER_NAME")
    main_folder_id = get_folder_id(main_folder_name)
    print(f"Main folder ID: {main_folder_id}")
    
    # Get or create Cleaned_Logs folder
    text_logs_folder_name = os.getenv("GDRIVE_CLEANED_LOGS_FOLDER", "Text_Logs")
    text_logs_folder_id = get_folder_id(text_logs_folder_name)
    
    # Get already processed sessions
    processed_sessions = get_processed_sessions(text_logs_folder_id)
    print(f"Already processed: {len(processed_sessions)} sessions")
    
    # Get all session folders
    all_session_folders = get_session_folders(main_folder_id)
    
    # Filter out already processed sessions
    unprocessed_folders = [
        folder for folder in all_session_folders 
        if folder['name'] not in processed_sessions
    ]
    
    print(f"Found {len(unprocessed_folders)} unprocessed session folders")
    
    # Limit to num_sessions
    session_folders = unprocessed_folders[:num_sessions]
    
    if not session_folders:
        print("\nNo unprocessed sessions found. All caught up!")
        return
    
    print(f"Processing {len(session_folders)} sessions (oldest first)")
    
    # Process each session
    for idx, session_folder in enumerate(session_folders, 1):
        print(f"\n{'=' * 60}")
        print(f"Processing Session {idx}/{len(session_folders)}: {session_folder['name']}")
        print(f"{'=' * 60}")
        
        session_dir = None
        try:
            # Download logs from this session
            downloaded_files, session_dir = download_session_logs(session_folder)
            
            # Clean and merge logs
            cleaned_events = merge_and_clean_logs(
                downloaded_files['pcap'],
                downloaded_files['browser'],
                downloaded_files['system']
            )
            
            if not cleaned_events:
                print(f"\nNo events to upload for session {session_folder['name']}")
                cleanup_temp_files(session_dir)
                continue
            
            # Upload cleaned logs with original session name
            upload_cleaned_logs(cleaned_events, session_folder['name'])
            
            # Cleanup temp files for this session
            cleanup_temp_files(session_dir)
            
        except Exception as e:
            print(f"\nError processing session {session_folder['name']}: {e}")
            if session_dir:
                cleanup_temp_files(session_dir)
            continue
    
    # Final cleanup
    if os.path.exists(TEMP_DOWNLOAD_DIR):
        cleanup_temp_files(TEMP_DOWNLOAD_DIR)
    
    print("\n" + "=" * 60)
    print("Processing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
