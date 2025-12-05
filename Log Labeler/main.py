"""Main script for labeling logs with MITRE ATT&CK techniques."""
import os
import sys
import json
import shutil
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Log Cleaner'))

from gdrive_helper import (
    get_folder_id, get_session_folders, get_files_in_folder,
    download_file, upload_file_from_content, create_folder,
    get_processed_sessions
)

load_dotenv()

TEMP_DOWNLOAD_DIR = "temp_text_logs"
TEMP_OUTPUT_DIR = "temp_labeled_logs"


def get_env_or_fail(var):
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value


def download_text_log(session_folder, text_logs_folder_id):
    print(f"\n=== Downloading text log from: {session_folder['name']} ===")
    
    session_dir = os.path.join(TEMP_DOWNLOAD_DIR, session_folder['name'])
    os.makedirs(session_dir, exist_ok=True)
    
    files = get_files_in_folder(session_folder['id'])
    
    text_log_path = None
    for file in files:
        file_name = file['name']
        if file_name.endswith('.json') and 'text_log' in file_name:
            print(f"Downloading: {file_name}")
            file_path = os.path.join(session_dir, file_name)
            download_file(file['id'], file_path)
            text_log_path = file_path
            break
    
    return text_log_path, session_dir


def filter_system_log(event):
    """Remove unnecessary fields from system logs while preserving structure."""
    filtered = {
        'timestamp': event.get('timestamp'),
        'event_type': event.get('event_type')
    }
    
    # Keep only essential winlog fields
    if 'winlog' in event:
        filtered['winlog'] = {
            'event_id': event['winlog'].get('event_id'),
            'task': event['winlog'].get('task')
        }
        
        # Keep only essential event_data fields
        if 'event_data' in event['winlog']:
            essential_fields = [
                'Image', 'ProcessId', 'ProcessGuid', 'User', 'CommandLine',
                'ParentImage', 'SourceIp', 'SourcePort', 'DestinationIp',
                'DestinationPort', 'Protocol', 'TargetFilename', 'TargetObject'
            ]
            filtered['winlog']['event_data'] = {}
            for field in essential_fields:
                if field in event['winlog']['event_data']:
                    filtered['winlog']['event_data'][field] = event['winlog']['event_data'][field]
    
    # Keep anonymized IDs
    if 'host_id' in event:
        filtered['host_id'] = event['host_id']
    if 'agent_id' in event:
        filtered['agent_id'] = event['agent_id']
    
    return filtered


def filter_network_log(event):
    """Remove unnecessary fields from network logs while preserving structure."""
    filtered = {
        'timestamp': event.get('timestamp'),
        'event_type': event.get('event_type'),
        'length': event.get('length'),
        'summary': event.get('summary'),
        'layers': {}
    }
    
    # Keep only essential IP layer fields
    if 'layers' in event and 'IP' in event['layers']:
        filtered['layers']['IP'] = {
            'src': event['layers']['IP'].get('src'),
            'dst': event['layers']['IP'].get('dst'),
            'proto': event['layers']['IP'].get('proto'),
            'ttl': event['layers']['IP'].get('ttl')
        }
    
    # Keep only essential TCP layer fields
    if 'layers' in event and 'TCP' in event['layers']:
        filtered['layers']['TCP'] = {
            'sport': event['layers']['TCP'].get('sport'),
            'dport': event['layers']['TCP'].get('dport'),
            'flags': event['layers']['TCP'].get('flags'),
            'seq': event['layers']['TCP'].get('seq'),
            'ack': event['layers']['TCP'].get('ack')
        }
    
    # Keep only essential UDP layer fields
    if 'layers' in event and 'UDP' in event['layers']:
        filtered['layers']['UDP'] = {
            'sport': event['layers']['UDP'].get('sport'),
            'dport': event['layers']['UDP'].get('dport')
        }
    
    return filtered


def filter_browser_log(event):
    """Remove unnecessary fields from browser logs while preserving structure."""
    filtered = {
        'timestamp': event.get('timestamp'),
        'event_type': event.get('event_type'),
        'duration': event.get('duration')
    }
    
    # Keep only essential data fields
    if 'data' in event:
        filtered['data'] = {
            'url': event['data'].get('url'),
            'title': event['data'].get('title'),
            'incognito': event['data'].get('incognito')
        }
    
    return filtered


def filter_log_entry(event):
    """Filter log entry based on event type, removing unnecessary fields."""
    event_type = event.get('event_type')
    
    if event_type == 'system':
        return filter_system_log(event)
    elif event_type == 'network':
        return filter_network_log(event)
    elif event_type == 'browser':
        return filter_browser_log(event)
    else:
        # Unknown type, return as-is
        return event


def label_logs(text_log_path, session_name):
    print("\n=== Starting Simple Log Labeling ===")
    
    try:
        with open(text_log_path, 'r', encoding='utf-8') as f:
            raw_events = json.load(f)
        
        # Ensure all events are dictionaries with required fields
        events = []
        for event in raw_events:
            if isinstance(event, dict):
                events.append(event)
            else:
                print(f"Warning: Skipping non-dictionary event of type {type(event)}")
                continue
        
        print(f"Total valid events: {len(events)} (from {len(raw_events)} total)")
        
        # Parse session_name to extract session_id and host_id
        # Use session_name as session_id, extract host_id from first event
        session_id = session_name
        host_id = None
        
        # Get host_id from the first event that has it
        for event in events:
            if 'host_id' in event and event['host_id']:
                host_id = event['host_id']
                break
        
        if not host_id and events:
            # Fallback to agent_id if host_id not found
            host_id = events[0].get('agent_id', 'unknown')
        
        # Process events into logs format with field filtering
        logs = []
        removed_system_fields = 0
        removed_network_fields = 0
        removed_browser_fields = 0
        
        for event in events:
            # Filter unnecessary fields based on event type
            filtered_event = filter_log_entry(event)
            
            # Count removed fields for statistics
            original_size = len(json.dumps(event))
            filtered_size = len(json.dumps(filtered_event))
            if filtered_size < original_size:
                event_type = event.get('event_type')
                if event_type == 'system':
                    removed_system_fields += 1
                elif event_type == 'network':
                    removed_network_fields += 1
                elif event_type == 'browser':
                    removed_browser_fields += 1
            
            # Add labels
            filtered_event["label"] = "normal"
            filtered_event["mitre_techniques"] = []
            logs.append(filtered_event)
        
        # Print statistics
        print(f"Field filtering statistics:")
        print(f"  - System logs filtered: {removed_system_fields}")
        print(f"  - Network logs filtered: {removed_network_fields}")
        print(f"  - Browser logs filtered: {removed_browser_fields}")
        
        # Sort logs by timestamp
        def parse_timestamp(log):
            ts = log.get("timestamp", "")
            if ts:
                try:
                    return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except ValueError:
                    return datetime.min
            return datetime.min
        
        logs.sort(key=parse_timestamp)
        
        # Create the final structure
        labeled_data = {
            "session_id": session_id,
            "host_id": host_id,
            "overall_label": "normal",
            "logs": logs
        }
        
        print(f"Created labeled data with {len(logs)} log entries")
        
        return labeled_data  # Return single object
    
    except Exception as e:
        print(f"Error labeling logs: {e}")
        return None


def save_labeled_logs_locally(labeled_data, session_name):
    output_dir = os.path.join(TEMP_OUTPUT_DIR, session_name)
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"annotation_{session_name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(labeled_data, f, indent=2)
    
    print(f"\nSaved locally:")
    print(f"  {output_file}")
    
    return output_dir


def upload_labeled_logs(labeled_data, session_name):
    print("\n=== Uploading to Google Drive ===")
    
    labeled_logs_folder_name = os.getenv("GDRIVE_LABELED_LOGS_FOLDER", "Labeled_Logs")
    labeled_logs_folder_id = get_folder_id(labeled_logs_folder_name)
    print(f"Labeled Logs folder ID: {labeled_logs_folder_id}")
    
    session_folder_id = create_folder(session_name, labeled_logs_folder_id)
    print(f"Created session folder: {session_name} (ID: {session_folder_id})")
    
    stories_file_name = f"annotated_data_{session_name}.json"
    stories_json = json.dumps(labeled_data, indent=2)
    upload_file_from_content(stories_json, session_folder_id, stories_file_name, mime_type='application/json')
    print(f"Uploaded: {stories_file_name}")


def cleanup_temp_files(temp_dir):
    if os.path.exists(temp_dir):
        print(f"\n=== Cleaning up temporary files ===")
        shutil.rmtree(temp_dir)
        print(f"Deleted: {temp_dir}")


def main():
    print("=" * 60)
    print("Log Labeler - MITRE ATT&CK Technique Detection")
    print("=" * 60)
    
    num_sessions = int(os.getenv("NUM_SESSIONS_TO_LABEL", "5"))
    print(f"\nProcessing up to {num_sessions} unlabeled sessions")
    
    text_logs_folder_name = get_env_or_fail("GDRIVE_TEXT_LOGS_FOLDER")
    text_logs_folder_id = get_folder_id(text_logs_folder_name)
    print(f"Text Logs folder ID: {text_logs_folder_id}")
    
    labeled_logs_folder_name = os.getenv("GDRIVE_LABELED_LOGS_FOLDER", "Labeled_Logs")
    labeled_logs_folder_id = get_folder_id(labeled_logs_folder_name)
    
    labeled_sessions = get_processed_sessions(labeled_logs_folder_id)
    print(f"Already labeled: {len(labeled_sessions)} sessions")
    
    all_text_sessions = get_session_folders(text_logs_folder_id)
    
    unlabeled_folders = [
        folder for folder in all_text_sessions 
        if folder['name'] not in labeled_sessions
    ]
    
    print(f"Found {len(unlabeled_folders)} unlabeled session folders")
    
    session_folders = unlabeled_folders[:num_sessions]
    
    if not session_folders:
        print("\nNo unlabeled sessions found. All caught up!")
        return
    
    print(f"Processing {len(session_folders)} sessions (oldest first)")
    
    for idx, session_folder in enumerate(session_folders, 1):
        print(f"\n{'=' * 60}")
        print(f"Processing Session {idx}/{len(session_folders)}: {session_folder['name']}")
        print(f"{'=' * 60}")
        
        text_log_path = None
        session_dir = None
        
        try:
            text_log_path, session_dir = download_text_log(session_folder, text_logs_folder_id)
            
            if not text_log_path:
                print(f"No text log found for session {session_folder['name']}")
                continue
            
            labeled_data = label_logs(text_log_path, session_folder['name'])
            
            if not labeled_data:
                print(f"No labeled data for session {session_folder['name']}")
                continue
            
            save_labeled_logs_locally(labeled_data, session_folder['name'])
            upload_labeled_logs(labeled_data, session_folder['name'])
            
            if session_dir:
                cleanup_temp_files(session_dir)
            
        except Exception as e:
            print(f"\nError processing session {session_folder['name']}: {e}")
            if session_dir:
                cleanup_temp_files(session_dir)
            continue
    
    for temp_dir in [TEMP_DOWNLOAD_DIR, TEMP_OUTPUT_DIR]:
        if os.path.exists(temp_dir):
            cleanup_temp_files(temp_dir)
    
    print("\n" + "=" * 60)
    print("Labeling Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
