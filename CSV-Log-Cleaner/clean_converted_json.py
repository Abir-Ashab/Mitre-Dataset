"""Clean converted JSON logs using the same methods as the Log Cleaner."""
import json
import sys
import hashlib
from datetime import datetime, timezone, timedelta


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


def anonymize_id(value):
    """Anonymize machine-specific IDs by hashing."""
    if value:
        return hashlib.md5(value.encode()).hexdigest()[:8]
    return None


def parse_and_clean_system_log(json_path):
    """Parse and clean system JSON log (JSONL format)."""
    events = []
    parsed_lines = 0
    skipped_lines = 0
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Processing {len(lines)} lines...")
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                log = json.loads(line)
                parsed_lines += 1
                raw_timestamp = log.get('@timestamp')
                timestamp = None
                
                if raw_timestamp:
                    try:
                        # Try Kibana format first (Jul 20, 2025 @ 20:54:59.842)
                        if isinstance(raw_timestamp, str) and '@' in raw_timestamp:
                            timestamp = parse_kibana_timestamp(raw_timestamp)
                        # Then try ISO format
                        elif isinstance(raw_timestamp, str):
                            if 'Z' in raw_timestamp:
                                ts_str = raw_timestamp.replace('Z', '+00:00')
                            elif '+' not in raw_timestamp and '-' not in raw_timestamp[10:]:
                                ts_str = raw_timestamp + '+00:00'
                            else:
                                ts_str = raw_timestamp
                            dt = datetime.fromisoformat(ts_str)
                            # Convert to UTC and format consistently
                            dt_utc = dt.astimezone(timezone.utc)
                            timestamp = dt_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                    except Exception as e:
                        if skipped_lines < 3:
                            print(f"Timestamp error on line {line_num}: {str(e)}")
                        timestamp = None
                
                # Preserve all data from the log
                event = {
                    'timestamp': timestamp,
                    'event_type': 'system'
                }
                # Add all fields from the log, excluding @timestamp if already processed
                for key, value in log.items():
                    if key != '@timestamp':
                        event[key] = value
                
                # Anonymize sensitive fields if present
                if log.get('host', {}).get('name'):
                    event['host_id'] = anonymize_id(log['host']['name'])
                if log.get('agent', {}).get('id'):
                    event['agent_id'] = anonymize_id(log['agent']['id'])
                    
                events.append(event)
                
                # Progress indicator for large files
                if parsed_lines % 5000 == 0:
                    print(f"  Processed {parsed_lines} lines...")
                    
            except json.JSONDecodeError as e:
                skipped_lines += 1
                if skipped_lines <= 3:  # Only show first 3 errors
                    print(f"Skipping invalid JSON on line {line_num}: {str(e)[:100]}")
                continue
            except Exception as e:
                skipped_lines += 1
                if skipped_lines <= 3:
                    print(f"Error processing line {line_num}: {str(e)[:100]}")
                continue
        
        print(f"\nParsed {len(events)} system log events from {parsed_lines} lines")
        if skipped_lines > 0:
            print(f"Skipped {skipped_lines} invalid/malformed lines")
    except Exception as e:
        print(f"Error parsing system log: {e}")
    return events


def remove_duplicates(events):
    """Identify exact duplicates while preserving event order and integrity."""
    print("\n=== Removing Duplicates ===")
    seen_events = set()
    unique_events = []
    duplicates = 0
    
    for event in events:
        # Create a frozen set of event items for hashing
        event_items = frozenset(
            (k, str(v)) for k, v in event.items() 
            if v is not None  # Ignore None values
        )
        
        if event_items not in seen_events:
            seen_events.add(event_items)
            unique_events.append(event)
        else:
            duplicates += 1
    
    if duplicates:
        print(f"Removed {duplicates} exact duplicate events")
    else:
        print("No duplicate events found")
    
    print(f"Events after deduplication: {len(unique_events)}")
    return unique_events


def standardize_timestamps(events):
    """Verify all timestamps are in ISO format with timezone (YYYY-MM-DDTHH:mm:ss.sssZ)."""
    print("\n=== Standardizing Timestamps ===")
    
    problematic_events = []
    valid_count = 0
    
    for event in events:
        timestamp = event.get('timestamp')
        if not timestamp:
            # Keep events without timestamp but mark them
            event['timestamp_error'] = 'No timestamp provided'
            problematic_events.append(event)
            continue
            
        # Verify timestamp is in correct format
        try:
            if isinstance(timestamp, str) and timestamp.endswith('Z'):
                # Try to parse it to verify it's valid
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                valid_count += 1
            else:
                # If not in expected format, try to convert it
                if isinstance(timestamp, (int, float)):
                    dt = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
                    event['timestamp'] = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                    valid_count += 1
                elif isinstance(timestamp, str):
                    # Try parsing as ISO format
                    if 'Z' in timestamp:
                        ts_str = timestamp.replace('Z', '+00:00')
                    elif '+' not in timestamp and '-' not in timestamp[10:]:
                        ts_str = timestamp + '+00:00'
                    else:
                        ts_str = timestamp
                    dt = datetime.fromisoformat(ts_str)
                    dt_utc = dt.astimezone(timezone.utc)
                    event['timestamp'] = dt_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                    valid_count += 1
                else:
                    event['timestamp_error'] = f'Unknown timestamp type: {type(timestamp)}'
                    problematic_events.append(event)
                    
        except Exception as e:
            event['timestamp_error'] = f'Failed to parse: {str(e)}'
            problematic_events.append(event)
    
    print(f"Timestamp Standardization Results:")
    print(f"- Valid timestamps: {valid_count}")
    if problematic_events:
        print(f"- Events with timestamp issues: {len(problematic_events)}")
        print("\nSample problematic timestamps:")
        for evt in problematic_events[:3]:  # Show first 3 examples
            print(f"  - Value: {evt.get('timestamp')} | Error: {evt.get('timestamp_error')}")
    
    return events


def filter_by_time_window(events, use_actual_range=True, window_minutes=None):
    """Filter events to a time window."""
    print("\n=== Analyzing Timestamp Range ===")
    
    # Analyze actual timestamp range in the logs
    valid_timestamps = []
    for event in events:
        ts = event.get('timestamp')
        if ts:
            try:
                event_dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                valid_timestamps.append(event_dt.replace(tzinfo=None))
            except:
                continue
    
    if not valid_timestamps:
        print("No valid timestamps found, skipping time filtering")
        return events
    
    min_ts = min(valid_timestamps)
    max_ts = max(valid_timestamps)
    duration = (max_ts - min_ts).total_seconds() / 60
    
    print(f"Actual log timestamp range:")
    print(f"  Earliest: {min_ts.isoformat()}")
    print(f"  Latest:   {max_ts.isoformat()}")
    print(f"  Duration: {duration:.1f} minutes")
    
    if use_actual_range:
        print("\nUsing actual log range (no filtering)")
        session_dt = min_ts
        session_end = max_ts
    elif window_minutes:
        print(f"\nFiltering to {window_minutes} minute window from earliest timestamp")
        session_dt = min_ts
        session_end = min_ts + timedelta(minutes=window_minutes)
    else:
        print("\nNo time filtering applied")
        return events
    
    # Filter events to time window
    filtered_events = []
    for event in events:
        try:
            ts = event.get('timestamp')
            if ts:
                event_dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                event_dt_naive = event_dt.replace(tzinfo=None)
                if session_dt <= event_dt_naive <= session_end:
                    filtered_events.append(event)
        except (ValueError, TypeError):
            continue
    
    print(f"Events in time window: {len(filtered_events)}")
    
    return filtered_events


def sort_by_timestamp(events):
    """Sort events by timestamp."""
    print("\n=== Sorting by Timestamp ===")
    
    events_sorted = sorted(events, key=lambda x: x.get('timestamp') or '')
    print(f"Sorted {len(events_sorted)} events")
    
    return events_sorted


def clean_system_json(input_file, output_file=None, time_filter=None):
    """
    Clean a system JSON log file.
    
    Args:
        input_file: Path to input JSON file (JSONL format)
        output_file: Path to output file (default: input_file with _cleaned suffix)
        time_filter: None (no filter), 'actual' (use actual range), or int (minutes from start)
    """
    print("=" * 60)
    print("System Log Cleaner")
    print("=" * 60)
    print(f"\nInput file: {input_file}")
    
    # Determine output file
    if not output_file:
        output_file = input_file.replace('.json', '_cleaned.json')
    print(f"Output file: {output_file}")
    
    # Parse and clean
    print("\n=== Parsing System Logs ===")
    events = parse_and_clean_system_log(input_file)
    
    if not events:
        print("\nNo events parsed. Exiting.")
        return
    
    print(f"\nTotal events parsed: {len(events)}")
    
    # Remove duplicates
    events = remove_duplicates(events)
    
    # Standardize timestamps
    events = standardize_timestamps(events)
    
    # Filter by time window
    if time_filter:
        if time_filter == 'actual':
            events = filter_by_time_window(events, use_actual_range=True)
        elif isinstance(time_filter, int):
            events = filter_by_time_window(events, use_actual_range=False, window_minutes=time_filter)
    
    # Sort by timestamp
    events = sort_by_timestamp(events)
    
    # Write output
    print("\n=== Writing Output ===")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully wrote {len(events)} events to {output_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Input events:    {len(events)} (after all processing)")
    print(f"Output file:     {output_file}")
    print(f"Processing:      Complete ✓")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_converted_json.py <input_json_file> [output_file] [time_filter]")
        print("\nArguments:")
        print("  input_json_file : Path to the JSON file to clean (JSONL format)")
        print("  output_file     : (Optional) Output file path (default: input_cleaned.json)")
        print("  time_filter     : (Optional) 'actual' (use actual time range) or minutes (e.g., 20)")
        print("\nExamples:")
        print('  python clean_converted_json.py "file.json"')
        print('  python clean_converted_json.py "file.json" "output.json"')
        print('  python clean_converted_json.py "file.json" "output.json" actual')
        print('  python clean_converted_json.py "file.json" "output.json" 20')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Parse time filter argument
    time_filter = None
    if len(sys.argv) > 3:
        filter_arg = sys.argv[3]
        if filter_arg == 'actual':
            time_filter = 'actual'
        else:
            try:
                time_filter = int(filter_arg)
            except ValueError:
                print(f"Warning: Invalid time_filter '{filter_arg}', ignoring")
    
    try:
        clean_system_json(input_file, output_file, time_filter)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
