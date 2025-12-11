"""
Script to filter annotated log files by removing unnecessary fields.
Creates filtered copies of JSON files from Pseudo-Annotated-Logs directory.
"""
import os
import json
import shutil
from datetime import datetime


def filter_system_log(event):
    """Remove unnecessary fields from system logs while preserving structure and labels."""
    import copy
    filtered = copy.deepcopy(event)
    
    # Remove unnecessary fields from winlog.event_data (metadata, not behavior traces)
    if 'winlog' in filtered and 'event_data' in filtered['winlog']:
        unnecessary_fields = [
            'UtcTime',  # Duplicates root timestamp
            'RuleName',  # Sysmon rule metadata
            'Hashes',  # Too detailed for initial filtering
            'IntegrityLevel',  # Windows metadata
            'TerminalSessionId',  # Windows session metadata
            'ParentProcessGuid', 'ParentProcessId',  # Redundant with ParentImage
            'ParentCommandLine',  # Often too verbose
            'CurrentDirectory',  # Low signal
            'SourceHostname', 'DestinationHostname',  # Redundant with IPs
            'SourceIsIpv6', 'DestinationIsIpv6',  # Can be inferred from IP
            'SourcePortName', 'DestinationPortName',  # Redundant with port number
            'Initiated'  # Usually always true
        ]
        for field in unnecessary_fields:
            filtered['winlog']['event_data'].pop(field, None)
    
    # Remove unnecessary top-level fields from winlog (infrastructure metadata)
    if 'winlog' in filtered:
        unnecessary_winlog_fields = [
            'api', 'computer_name', 'opcode', 'process', 'provider_guid',
            'provider_name', 'record_id', 'version', 'channel', 'keywords',
            'task',  # Verbose description, duplicates event_id
            'user'  # Contains SID and domain, redundant with event_data.User
        ]
        for field in unnecessary_winlog_fields:
            filtered['winlog'].pop(field, None)
    
    # Remove top-level infrastructure fields (not behavior traces)
    unnecessary_top_fields = [
        '@timestamp',  # Use 'timestamp' instead
        '@version',  # Logstash version
        'message',  # Duplicates event_data in string format
        'log',  # Log metadata
        'ecs',  # ECS schema version
        'host',  # Use host_id instead
        'agent',  # Use agent_id instead
        'tags',  # Logstash processing tags
        'event'  # Contains duplicates like event.original, event.created
    ]
    for field in unnecessary_top_fields:
        filtered.pop(field, None)
    
    return filtered


def filter_network_log(event):
    """Remove unnecessary fields from network logs while preserving structure and labels."""
    import copy
    filtered = copy.deepcopy(event)
    
    # Remove infrastructure/metadata fields (not behavior traces)
    unnecessary_top_fields = [
        'packet_number',  # Sequential numbering, not temporal
        'raw_hex'  # Full packet bytes, too large for ML
    ]
    for field in unnecessary_top_fields:
        filtered.pop(field, None)
    
    # Remove entire Ethernet layer (MAC addresses, not behavior)
    if 'layers' in filtered:
        filtered['layers'].pop('Ether', None)
    
    # Remove unnecessary fields from IP layer (infrastructure details)
    if 'layers' in filtered and 'IP' in filtered['layers']:
        unnecessary_ip_fields = [
            'version',  # Always 4 (IPv4)
            'ihl',  # IP header length
            'tos',  # Type of service, rarely used
            'len',  # Duplicates root 'length'
            'id',  # IP identification for fragmentation
            'flags',  # IP flags (DF), rarely relevant
            'frag',  # Fragment offset
            'chksum',  # Error detection only
            'options'  # Usually empty
        ]
        for field in unnecessary_ip_fields:
            filtered['layers']['IP'].pop(field, None)
    
    # Remove unnecessary fields from TCP layer (infrastructure details)
    if 'layers' in filtered and 'TCP' in filtered['layers']:
        unnecessary_tcp_fields = [
            'dataofs',  # TCP data offset/header size
            'reserved',  # Reserved bits, always 0
            'window',  # Flow control, not attack indicator
            'chksum',  # Error detection only
            'urgptr',  # Urgent pointer, rarely used
            'options'  # Usually empty
        ]
        for field in unnecessary_tcp_fields:
            filtered['layers']['TCP'].pop(field, None)
    
    # Remove unnecessary fields from UDP layer (infrastructure details)
    if 'layers' in filtered and 'UDP' in filtered['layers']:
        unnecessary_udp_fields = [
            'len',  # Duplicates packet length
            'chksum'  # Error detection only
        ]
        for field in unnecessary_udp_fields:
            filtered['layers']['UDP'].pop(field, None)
    
    # Remove raw payload data (not needed for behavioral analysis)
    if 'layers' in filtered:
        filtered['layers'].pop('Raw', None)
        filtered['layers'].pop('Padding', None)
    
    return filtered


def filter_browser_log(event):
    """Remove unnecessary fields from browser logs while preserving structure and labels."""
    import copy
    filtered = copy.deepcopy(event)
    
    # Remove infrastructure/metadata fields (not behavior traces)
    unnecessary_top_fields = [
        'id'  # ActivityWatch internal event ID, not temporal
    ]
    for field in unnecessary_top_fields:
        filtered.pop(field, None)
    
    # Remove unnecessary fields from browser data (not security relevant)
    if 'data' in filtered:
        unnecessary_data_fields = [
            'audible',  # Whether page made sound, not security relevant
            'tabId', 'windowId', 'frameId',  # Browser internal IDs
            'transitionType', 'transitionQualifiers',  # Navigation metadata
            'referrer',  # Can be useful but often redundant
            'tabCount'  # Weak signal
        ]
        for field in unnecessary_data_fields:
            filtered['data'].pop(field, None)
    
    return filtered


def filter_log_entry(event):
    """Filter log entry based on event type, removing unnecessary fields."""
    import copy
    event_type = event.get('event_type')
    
    if event_type == 'system':
        return filter_system_log(event)
    elif event_type == 'network':
        return filter_network_log(event)
    elif event_type == 'browser':
        return filter_browser_log(event)
    else:
        # Unknown type, return as-is (just deep copy)
        return copy.deepcopy(event)


def filter_json_file(input_path, output_path):
    """
    Filter a single JSON file by removing unnecessary fields from log entries.
    
    Args:
        input_path: Path to the input JSON file
        output_path: Path to save the filtered JSON file
    
    Returns:
        Dictionary with statistics about the filtering process
    """
    print(f"\nProcessing: {os.path.basename(input_path)}")
    
    try:
        # Read the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Preserve top-level structure
        filtered_data = {
            'session_id': data.get('session_id'),
            'host_id': data.get('host_id'),
            'overall_label': data.get('overall_label'),
            'logs': []
        }
        
        # Filter each log entry
        original_logs = data.get('logs', [])
        stats = {
            'total_logs': len(original_logs),
            'system_logs': 0,
            'network_logs': 0,
            'browser_logs': 0,
            'other_logs': 0,
            'original_size_mb': 0,
            'filtered_size_mb': 0
        }
        
        for log_entry in original_logs:
            filtered_entry = filter_log_entry(log_entry)
            filtered_data['logs'].append(filtered_entry)
            
            # Count by type
            event_type = log_entry.get('event_type')
            if event_type == 'system':
                stats['system_logs'] += 1
            elif event_type == 'network':
                stats['network_logs'] += 1
            elif event_type == 'browser':
                stats['browser_logs'] += 1
            else:
                stats['other_logs'] += 1
        
        # Calculate sizes
        original_size = os.path.getsize(input_path)
        stats['original_size_mb'] = round(original_size / (1024 * 1024), 2)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the filtered data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=2)
        
        # Calculate filtered size
        filtered_size = os.path.getsize(output_path)
        stats['filtered_size_mb'] = round(filtered_size / (1024 * 1024), 2)
        stats['reduction_percent'] = round(
            ((original_size - filtered_size) / original_size) * 100, 2
        )
        
        print(f"  Total logs: {stats['total_logs']}")
        print(f"    - System: {stats['system_logs']}")
        print(f"    - Network: {stats['network_logs']}")
        print(f"    - Browser: {stats['browser_logs']}")
        if stats['other_logs'] > 0:
            print(f"    - Other: {stats['other_logs']}")
        print(f"  Original size: {stats['original_size_mb']} MB")
        print(f"  Filtered size: {stats['filtered_size_mb']} MB")
        print(f"  Reduction: {stats['reduction_percent']}%")
        
        return stats
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def process_all_sessions(input_base_dir, output_base_dir):
    """
    Process all session folders in the Pseudo-Annotated-Logs directory.
    
    Args:
        input_base_dir: Base directory containing session folders
        output_base_dir: Base directory for filtered output
    """
    print("=" * 70)
    print("Annotated Logs Filtering Script")
    print("=" * 70)
    print(f"\nInput directory: {input_base_dir}")
    print(f"Output directory: {output_base_dir}")
    
    if not os.path.exists(input_base_dir):
        print(f"\nERROR: Input directory does not exist: {input_base_dir}")
        return
    
    # Get all session folders
    session_folders = [
        f for f in os.listdir(input_base_dir)
        if os.path.isdir(os.path.join(input_base_dir, f))
    ]
    
    if not session_folders:
        print("\nNo session folders found.")
        return
    
    print(f"\nFound {len(session_folders)} session folders")
    
    # Process each session folder
    overall_stats = {
        'processed': 0,
        'failed': 0,
        'total_original_mb': 0,
        'total_filtered_mb': 0
    }
    
    for session_folder in sorted(session_folders):
        print(f"\n{'=' * 70}")
        print(f"Session: {session_folder}")
        print('=' * 70)
        
        input_session_dir = os.path.join(input_base_dir, session_folder)
        output_session_dir = os.path.join(output_base_dir, session_folder)
        
        # Find JSON files in the session folder
        json_files = [
            f for f in os.listdir(input_session_dir)
            if f.endswith('.json')
        ]
        
        if not json_files:
            print("No JSON files found in this session folder")
            continue
        
        # Process each JSON file
        for json_file in json_files:
            input_path = os.path.join(input_session_dir, json_file)
            
            # Create output filename with "_filtered" suffix
            base_name = os.path.splitext(json_file)[0]
            output_filename = f"{base_name}_filtered.json"
            output_path = os.path.join(output_session_dir, output_filename)
            
            stats = filter_json_file(input_path, output_path)
            
            if stats:
                overall_stats['processed'] += 1
                overall_stats['total_original_mb'] += stats['original_size_mb']
                overall_stats['total_filtered_mb'] += stats['filtered_size_mb']
            else:
                overall_stats['failed'] += 1
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print('=' * 70)
    print(f"Files processed successfully: {overall_stats['processed']}")
    print(f"Files failed: {overall_stats['failed']}")
    print(f"Total original size: {round(overall_stats['total_original_mb'], 2)} MB")
    print(f"Total filtered size: {round(overall_stats['total_filtered_mb'], 2)} MB")
    
    if overall_stats['total_original_mb'] > 0:
        reduction = (
            (overall_stats['total_original_mb'] - overall_stats['total_filtered_mb'])
            / overall_stats['total_original_mb']
        ) * 100
        print(f"Overall reduction: {round(reduction, 2)}%")
        print(f"Space saved: {round(overall_stats['total_original_mb'] - overall_stats['total_filtered_mb'], 2)} MB")
    
    print(f"\nFiltered files saved to: {output_base_dir}")


def main():
    """Main entry point for the script."""
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_base_dir = os.path.join(project_root, "Pseudo-Annotated-Logs")
    output_base_dir = os.path.join(project_root, "Pseudo-Annotated-Logs-Filtered")
    
    # Process all sessions
    process_all_sessions(input_base_dir, output_base_dir)
    
    print("\n" + "=" * 70)
    print("Filtering Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
