"""Annotate network logs with the same structure as Log Labeler."""
import json
import sys
import copy
from datetime import datetime


def filter_network_log(event):
    """Remove unnecessary fields from network logs while preserving structure and labels."""
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


def parse_timestamp(log):
    """Parse timestamp for sorting."""
    ts = log.get("timestamp", "")
    if ts:
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            return datetime.min
    return datetime.min


def annotate_network_logs(input_file, output_file=None, session_id=None):
    """
    Annotate network logs with labels and MITRE techniques.
    
    Args:
        input_file: Path to converted JSON file (JSONL format)
        output_file: Path to output file (default: input_file with _annotated suffix)
        session_id: Session identifier (default: extracted from filename or timestamp)
    """
    print("=" * 60)
    print("Network Log Annotator")
    print("=" * 60)
    print(f"\nInput file: {input_file}")
    
    # Determine output file
    if not output_file:
        output_file = input_file.replace('.json', '_annotated.json')
    print(f"Output file: {output_file}")
    
    # Load the converted logs (JSONL format)
    print("\n=== Loading Logs ===")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        raw_events = []
        for line in lines:
            if line.strip():
                raw_events.append(json.loads(line))
        
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
    
    # Determine session_id
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
                    session_id = "network_capture"
            else:
                session_id = "network_capture"
    
    print(f"Session ID: {session_id}")
    
    # For network logs, we don't have host_id from the logs themselves
    # Generate a generic one or use unknown
    host_id = "network_host"
    print(f"Host ID: {host_id}")
    
    # Process events with field filtering and labeling
    print("\n=== Processing Events ===")
    logs = []
    filtered_count = 0
    
    for event in events:
        # Filter unnecessary fields
        filtered_event = filter_network_log(event)
        
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
        print("Usage: python annotate_network_logs.py <input_json_file> [output_file] [session_id]")
        print("\nArguments:")
        print("  input_json_file : Path to the converted JSON file (JSONL format)")
        print("  output_file     : (Optional) Output file path (default: input_annotated.json)")
        print("  session_id      : (Optional) Session identifier (default: auto-detect from filename/timestamp)")
        print("\nExamples:")
        print('  python annotate_network_logs.py "traffic_converted.json"')
        print('  python annotate_network_logs.py "traffic_converted.json" "annotated.json"')
        print('  python annotate_network_logs.py "traffic_converted.json" "annotated.json" "20251022_123000"')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    session_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        annotate_network_logs(input_file, output_file, session_id)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
