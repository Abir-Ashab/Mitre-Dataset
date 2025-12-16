"""Annotate system logs with the same structure as Log Labeler."""
import json
import sys
import copy
from datetime import datetime


def filter_system_log(event):
    """Remove unnecessary fields from system logs while preserving structure and labels."""
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


def parse_timestamp(log):
    """Parse timestamp for sorting."""
    ts = log.get("timestamp", "")
    if ts:
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            return datetime.min
    return datetime.min


def annotate_system_logs(input_file, output_file=None, session_id=None):
    """
    Annotate system logs with labels and MITRE techniques.
    
    Args:
        input_file: Path to cleaned JSON file (array format)
        output_file: Path to output file (default: input_file with _annotated suffix)
        session_id: Session identifier (default: extracted from filename or timestamp)
    """
    print("=" * 60)
    print("System Log Annotator")
    print("=" * 60)
    print(f"\nInput file: {input_file}")
    
    # Determine output file
    if not output_file:
        output_file = input_file.replace('.json', '_annotated.json')
    print(f"Output file: {output_file}")
    
    # Load the cleaned logs
    print("\n=== Loading Logs ===")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_events = json.load(f)
        print(f"Loaded {len(raw_events)} events")
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Ensure all events are dictionaries with required fields
    events = []
    for event in raw_events:
        if isinstance(event, dict):
            events.append(event)
        else:
            print(f"Warning: Skipping non-dictionary event of type {type(event)}")
            continue
    
    print(f"Valid events: {len(events)} (from {len(raw_events)} total)")
    
    # Determine session_id and host_id
    if not session_id:
        # Try to extract from filename
        import os
        filename = os.path.basename(input_file)
        # Look for date pattern YYYYMMDD_HHMMSS
        import re
        match = re.search(r'\d{8}_\d{6}', filename)
        if match:
            session_id = match.group(0)
        else:
            # Use first timestamp
            if events and events[0].get('timestamp'):
                try:
                    dt = datetime.fromisoformat(events[0]['timestamp'].replace('Z', '+00:00'))
                    session_id = dt.strftime('%Y%m%d_%H%M%S')
                except:
                    session_id = "unknown_session"
            else:
                session_id = "unknown_session"
    
    print(f"Session ID: {session_id}")
    
    # Get host_id from the first event that has it
    host_id = None
    for event in events:
        if 'host_id' in event and event['host_id']:
            host_id = event['host_id']
            break
    
    if not host_id and events:
        # Fallback to agent_id if host_id not found
        host_id = events[0].get('agent_id', 'unknown')
    
    print(f"Host ID: {host_id}")
    
    # Process events with field filtering and labeling
    print("\n=== Processing Events ===")
    logs = []
    filtered_count = 0
    
    for event in events:
        # Filter unnecessary fields
        filtered_event = filter_system_log(event)
        
        # Count if fields were removed
        original_size = len(json.dumps(event))
        filtered_size = len(json.dumps(filtered_event))
        if filtered_size < original_size:
            filtered_count += 1
        
        # Add labels
        filtered_event["label"] = "normal"
        filtered_event["mitre_techniques"] = []
        logs.append(filtered_event)
    
    print(f"Events filtered: {filtered_count}")
    
    # Sort logs by timestamp
    print("\n=== Sorting by Timestamp ===")
    logs.sort(key=parse_timestamp)
    print(f"Sorted {len(logs)} log entries")
    
    # Create the final structure
    annotated_data = {
        "session_id": session_id,
        "host_id": host_id,
        "overall_label": "normal",
        "logs": logs
    }
    
    # Write output
    print("\n=== Writing Output ===")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(annotated_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully wrote annotated data to {output_file}")
    except Exception as e:
        print(f"Error writing output: {e}")
        return
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Session ID:      {session_id}")
    print(f"Host ID:         {host_id}")
    print(f"Total logs:      {len(logs)}")
    print(f"Overall label:   normal")
    print(f"Output file:     {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python annotate_system_logs.py <input_json_file> [output_file] [session_id]")
        print("\nArguments:")
        print("  input_json_file : Path to the cleaned JSON file (array format)")
        print("  output_file     : (Optional) Output file path (default: input_annotated.json)")
        print("  session_id      : (Optional) Session identifier (default: auto-detect from filename/timestamp)")
        print("\nExamples:")
        print('  python annotate_system_logs.py "cleaned_logs.json"')
        print('  python annotate_system_logs.py "cleaned_logs.json" "annotated.json"')
        print('  python annotate_system_logs.py "cleaned_logs.json" "annotated.json" "20251022_123000"')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    session_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        annotate_system_logs(input_file, output_file, session_id)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
