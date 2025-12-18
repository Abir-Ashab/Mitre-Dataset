"""
Convert all browser logs in Google Drive from buckets format to flat array format.

This script will:
1. Connect to Google Drive
2. Go through each folder in the specified parent folder
3. Find browser log files (aw-buckets-export.json or similar)
4. Convert from nested buckets format to flat array format
5. Upload the converted files back to Google Drive (replacing the original)
"""

import json
import os
import sys
import io
from dotenv import load_dotenv
from googleapiclient.http import MediaIoBaseUpload
from gdrive_helper import (
    authenticate, get_folder_id, get_session_folders, 
    get_files_in_folder, download_file, upload_file_from_content
)

load_dotenv()

TEMP_DIR = "temp_browser_conversion"


def convert_browser_log_data(data):
    """
    Convert browser log data from nested buckets format to flat array format.
    
    Args:
        data: Parsed JSON data
    
    Returns:
        List of events with id field added, or None if already in correct format
    """
    # Check if it's already in the correct format (flat array)
    if isinstance(data, list):
        print(f"  Already in correct format (flat array with {len(data)} events)")
        return None
    
    # Extract events from buckets format
    events = []
    
    if isinstance(data, dict):
        # Check if it has "buckets" key
        if "buckets" in data:
            buckets = data["buckets"]
            for bucket_name, bucket_data in buckets.items():
                if isinstance(bucket_data, dict) and "events" in bucket_data:
                    events.extend(bucket_data["events"])
                    print(f"  Extracted {len(bucket_data['events'])} events from bucket: {bucket_name}")
        # Check if it's a direct bucket (without "buckets" wrapper)
        elif any(isinstance(v, dict) and "events" in v for v in data.values()):
            for bucket_name, bucket_data in data.items():
                if isinstance(bucket_data, dict) and "events" in bucket_data:
                    events.extend(bucket_data["events"])
                    print(f"  Extracted {len(bucket_data['events'])} events from bucket: {bucket_name}")
        else:
            print("  Warning: Unexpected data format - no events found")
            return None
    else:
        print(f"  Warning: Unexpected data type: {type(data)}")
        return None
    
    if not events:
        print("  Warning: No events found in the file")
        return None
    
    # Sort events by timestamp (newest first)
    events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Add sequential ID to each event after sorting
    for idx, event in enumerate(events, start=1):
        event["id"] = idx
    
    return events


def process_browser_log(file_info, folder_id, session_name):
    """
    Download, convert, and re-upload a browser log file.
    
    Args:
        file_info: Dictionary with file id and name
        folder_id: Parent folder ID in Google Drive
        session_name: Name of the session folder
    
    Returns:
        True if conversion was performed, False otherwise
    """
    file_name = file_info['name']
    file_id = file_info['id']
    
    print(f"\n  Processing: {file_name}")
    
    # Download the file
    os.makedirs(TEMP_DIR, exist_ok=True)
    local_path = os.path.join(TEMP_DIR, file_name)
    
    try:
        print(f"  Downloading... (this may take a moment for large files)")
        download_file(file_id, local_path)
        
        # Check file size
        file_size = os.path.getsize(local_path) / (1024 * 1024)  # MB
        print(f"  Downloaded {file_size:.2f} MB")
        
        # Read and parse JSON
        with open(local_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert the data
        converted_events = convert_browser_log_data(data)
        
        if converted_events is None:
            print(f"  Skipped: No conversion needed")
            return False
        
        # Upload converted file back to Google Drive (update in place)
        converted_json = json.dumps(converted_events, indent=4, ensure_ascii=False)
        
        # Update the existing file instead of deleting
        service = authenticate()
        
        media = MediaIoBaseUpload(
            io.BytesIO(converted_json.encode('utf-8')),
            mimetype='application/json',
            resumable=True
        )
        
        service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        
        print(f"  ✓ Updated file with converted data ({len(converted_events)} events)")
        
        # Clean up local file
        os.remove(local_path)
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"  Error: Invalid JSON format - {e}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    """Main function to process all browser logs in Google Drive."""
    # Get folder name from environment
    folder_name = os.getenv('GDRIVE_FOLDER_NAME')
    if not folder_name:
        print("Error: GDRIVE_FOLDER_NAME not set in .env file")
        sys.exit(1)
    
    print("=" * 70)
    print("Browser Log Format Converter - Google Drive Batch Processing")
    print("=" * 70)
    print(f"\nTarget folder: {folder_name}")
    
    # Get the main folder ID
    try:
        main_folder_id = get_folder_id(folder_name)
        print(f"Main folder ID: {main_folder_id}")
    except Exception as e:
        print(f"Error: Could not find folder '{folder_name}': {e}")
        sys.exit(1)
    
    # Get all session folders
    print("\nFetching session folders...")
    session_folders = get_session_folders(main_folder_id, limit=None)
    print(f"Found {len(session_folders)} session folders")
    
    # Process each session folder
    total_converted = 0
    total_skipped = 0
    total_errors = 0
    
    for idx, session_folder in enumerate(session_folders, start=1):
        session_name = session_folder['name']
        folder_id = session_folder['id']
        
        print(f"\n{'=' * 70}")
        print(f"Processing Session {idx}/{len(session_folders)}: {session_name}")
        print(f"{'=' * 70}")
        
        # Get all files in the session folder
        files = get_files_in_folder(folder_id)
        
        # Find browser log files
        browser_files = []
        for file in files:
            file_name_lower = file['name'].lower()
            if any(keyword in file_name_lower for keyword in ['aw-buckets', 'browser', 'activitywatch']):
                if file_name_lower.endswith('.json'):
                    browser_files.append(file)
        
        if not browser_files:
            print(f"  No browser log files found")
            total_skipped += 1
            continue
        
        print(f"  Found {len(browser_files)} browser log file(s)")
        
        # Process each browser log file
        session_converted = False
        for browser_file in browser_files:
            try:
                converted = process_browser_log(browser_file, folder_id, session_name)
                if converted:
                    session_converted = True
            except KeyboardInterrupt:
                print(f"\n  Interrupted by user. Stopping...")
                raise
            except Exception as e:
                print(f"  Error processing {browser_file['name']}: {str(e)[:200]}")
                import traceback
                print(f"  Details: {traceback.format_exc()[:500]}")
                total_errors += 1
                continue
        
        if session_converted:
            total_converted += 1
        else:
            total_skipped += 1
    
    # Clean up temp directory
    if os.path.exists(TEMP_DIR):
        import shutil
        shutil.rmtree(TEMP_DIR)
    
    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total sessions processed: {len(session_folders)}")
    print(f"Sessions with conversions: {total_converted}")
    print(f"Sessions skipped/no conversion needed: {total_skipped}")
    print(f"Errors encountered: {total_errors}")
    print(f"{'=' * 70}")
    print("\nConversion completed!")


if __name__ == "__main__":
    main()
