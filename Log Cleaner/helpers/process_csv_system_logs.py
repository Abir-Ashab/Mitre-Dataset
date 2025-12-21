"""Script to process CSV system log files from Google Drive folders.
Downloads CSV files, converts them to JSON, and merges multiple CSVs if present."""
import os
import csv
import json
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from gdrive_helper import authenticate, get_folder_id, download_file

load_dotenv()


def parse_kibana_timestamp(timestamp_str):
    """Parse Kibana timestamp format: Jul 20, 2025 @ 20:54:59.842"""
    try:
        # Remove the '@' and parse
        timestamp_str = timestamp_str.replace(' @ ', ' ')
        dt = datetime.strptime(timestamp_str, '%b %d, %Y %H:%M:%S.%f')
        # Return as ISO format with Z
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    except Exception as e:
        return None


def convert_csv_row_to_json(row):
    """Convert a single CSV row to JSON format matching syslog structure."""
    log_entry = {}
    
    # Timestamp - parse and convert Kibana format
    if row.get('@timestamp'):
        parsed_ts = parse_kibana_timestamp(row['@timestamp'])
        log_entry['@timestamp'] = parsed_ts if parsed_ts else row['@timestamp']
    
    # Agent information
    agent = {}
    if row.get('agent.name'):
        agent['name'] = row['agent.name']
    if row.get('agent.ephemeral_id'):
        agent['ephemeral_id'] = row['agent.ephemeral_id']
    if row.get('agent.version'):
        agent['version'] = row['agent.version']
    if row.get('agent.id'):
        agent['id'] = row['agent.id']
    if row.get('agent.type'):
        agent['type'] = row['agent.type']
    if agent:
        log_entry['agent'] = agent
    
    # Host information
    host = {}
    if row.get('host.name'):
        host['name'] = row['host.name']
    if host:
        log_entry['host'] = host
    
    # Winlog information
    winlog = {}
    
    # Basic winlog fields
    if row.get('winlog.provider_guid'):
        winlog['provider_guid'] = row['winlog.provider_guid']
    if row.get('winlog.opcode'):
        winlog['opcode'] = row['winlog.opcode']
    if row.get('winlog.record_id'):
        try:
            winlog['record_id'] = int(row['winlog.record_id'])
        except:
            winlog['record_id'] = row['winlog.record_id']
    if row.get('winlog.provider_name'):
        winlog['provider_name'] = row['winlog.provider_name']
    if row.get('winlog.task'):
        winlog['task'] = row['winlog.task']
    if row.get('winlog.computer_name'):
        winlog['computer_name'] = row['winlog.computer_name']
    if row.get('winlog.event_id'):
        winlog['event_id'] = row['winlog.event_id']
    if row.get('winlog.channel'):
        winlog['channel'] = row['winlog.channel']
    if row.get('winlog.keywords'):
        winlog['keywords'] = row['winlog.keywords']
    
    # Winlog user information
    user = {}
    if row.get('winlog.user.name'):
        user['name'] = row['winlog.user.name']
    if row.get('winlog.user.type'):
        user['type'] = row['winlog.user.type']
    if row.get('winlog.user.identifier'):
        user['identifier'] = row['winlog.user.identifier']
    if row.get('winlog.user.domain'):
        user['domain'] = row['winlog.user.domain']
    if user:
        winlog['user'] = user
    
    # Winlog process information
    process = {}
    if row.get('winlog.process.pid'):
        try:
            process['pid'] = int(row['winlog.process.pid'])
        except:
            process['pid'] = row['winlog.process.pid']
    
    thread = {}
    if row.get('winlog.process.thread.id'):
        try:
            thread['id'] = int(row['winlog.process.thread.id'])
        except:
            thread['id'] = row['winlog.process.thread.id']
    if thread:
        process['thread'] = thread
    if process:
        winlog['process'] = process
    
    # Winlog event_data - dynamically capture all event_data fields
    event_data = {}
    for key, value in row.items():
        if key and key.startswith('winlog.event_data.') and value:
            field_name = key.replace('winlog.event_data.', '')
            # Skip .keyword fields
            if not field_name.endswith('.keyword'):
                event_data[field_name] = value
    
    if event_data:
        winlog['event_data'] = event_data
    
    if winlog:
        log_entry['winlog'] = winlog
    
    # Version
    if row.get('@version'):
        try:
            log_entry['@version'] = str(int(row['@version']))
        except:
            log_entry['@version'] = row['@version']
    
    # ECS
    ecs = {}
    if row.get('ecs.version'):
        ecs['version'] = row['ecs.version']
    if ecs:
        log_entry['ecs'] = ecs
    
    # Log level
    log = {}
    if row.get('log.level'):
        log['level'] = row['log.level']
    if log:
        log_entry['log'] = log
    
    # Event information
    event = {}
    if row.get('event.kind'):
        event['kind'] = row['event.kind']
    if row.get('event.original'):
        event['original'] = row['event.original']
    if row.get('event.created'):
        event['created'] = row['event.created']
    if row.get('event.code'):
        event['code'] = row['event.code']
    if row.get('event.action'):
        event['action'] = row['event.action']
    if row.get('event.provider'):
        event['provider'] = row['event.provider']
    if row.get('event.outcome'):
        event['outcome'] = row['event.outcome']
    if event:
        log_entry['event'] = event
    
    # Tags
    if row.get('tags'):
        tags = row['tags']
        # If tags is a string, try to parse it as list
        if tags:
            try:
                log_entry['tags'] = json.loads(tags) if tags.startswith('[') else [tags]
            except:
                log_entry['tags'] = [tags]
    
    # Message
    if row.get('message'):
        log_entry['message'] = row['message']
    
    return log_entry


def convert_csv_files_to_json(csv_files, output_file):
    """
    Convert one or more CSV files to JSON format.
    If multiple CSV files are provided, merge them into one JSON.
    """
    all_entries = []
    
    for csv_file in csv_files:
        print(f"  Processing: {os.path.basename(csv_file)}")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                log_entry = convert_csv_row_to_json(row)
                all_entries.append(log_entry)
        
        print(f"    ✓ Read {len(all_entries)} entries so far")
    
    # Write to output file (JSONL format)
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"  ✓ Wrote {len(all_entries)} total entries to {os.path.basename(output_file)}")
    return len(all_entries)


def get_all_folders(parent_folder_id, limit=None):
    """Get folders from Google Drive sorted by creation time."""
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
    
    if limit:
        return all_folders[:limit]
    return all_folders


def get_files_in_folder(folder_id):
    """Get all files in a folder."""
    service = authenticate()
    
    files = []
    page_token = None
    
    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name, mimeType), nextPageToken',
            pageToken=page_token
        ).execute()
        
        files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    return files


def upload_file(file_path, folder_id):
    """Upload a file to Google Drive folder."""
    service = authenticate()
    
    from googleapiclient.http import MediaFileUpload
    
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name'
    ).execute()
    
    return file


def process_folder(folder_id, folder_name, temp_dir):
    """Process a single folder: download CSV files, convert to JSON, upload result."""
    print(f"\n→ Processing folder: {folder_name}")
    
    # Get all files in folder
    files = get_files_in_folder(folder_id)
    
    # Filter CSV files
    csv_files = [f for f in files if f['name'].lower().endswith('.csv')]
    
    if not csv_files:
        print("  • No CSV files found")
        return 0
    
    print(f"  Found {len(csv_files)} CSV file(s)")
    
    # Create folder-specific temp directory
    folder_temp_dir = os.path.join(temp_dir, folder_name)
    os.makedirs(folder_temp_dir, exist_ok=True)
    
    # Download all CSV files
    downloaded_files = []
    for csv_file in csv_files:
        local_path = os.path.join(folder_temp_dir, csv_file['name'])
        print(f"  Downloading: {csv_file['name']}")
        download_file(csv_file['id'], local_path)
        downloaded_files.append(local_path)
    
    # Convert and merge CSVs to JSON
    output_filename = f"syslogs_{folder_name}.json"
    output_path = os.path.join(folder_temp_dir, output_filename)
    
    print(f"  Converting to JSON...")
    total_entries = convert_csv_files_to_json(downloaded_files, output_path)
    
    # Upload result to Google Drive
    print(f"  Uploading result: {output_filename}")
    uploaded = upload_file(output_path, folder_id)
    print(f"  ✓ Uploaded: {uploaded['name']}")
    
    # Clean up temporary files
    for file in downloaded_files:
        os.remove(file)
    os.remove(output_path)
    
    return total_entries


def main():
    """Main function to process CSV system logs from folders."""
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
    
    # Create temporary directory for downloads
    temp_dir = tempfile.mkdtemp(prefix='csv_processing_')
    print(f"Using temporary directory: {temp_dir}")
    
    # Process each folder
    print("\n" + "="*60)
    print("STARTING CSV PROCESSING")
    print("="*60)
    
    total_entries = 0
    processed_folders = 0
    failed_folders = 0
    
    for i, folder in enumerate(folders, 1):
        try:
            print(f"\n[{i}/{len(folders)}] {folder['name']}")
            entries = process_folder(folder['id'], folder['name'], temp_dir)
            total_entries += entries
            processed_folders += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed_folders += 1
            import traceback
            traceback.print_exc()
    
    # Clean up temp directory
    try:
        os.rmdir(temp_dir)
    except:
        pass
    
    # Summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Folders processed: {processed_folders}")
    print(f"Total log entries converted: {total_entries}")
    print(f"Failed folders: {failed_folders}")
    print("="*60)


if __name__ == "__main__":
    main()
