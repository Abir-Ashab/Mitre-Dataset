"""Log parsing functions for different log types."""
import json
import os
import hashlib
import subprocess
import tempfile


def anonymize_id(value):
    """Anonymize machine-specific IDs by hashing."""
    if value:
        return hashlib.md5(value.encode()).hexdigest()[:8]
    return None


def parse_browser_logs(browser_path):
    """Parse ActivityWatch browser JSON log."""
    from datetime import datetime, timezone
    events = []
    try:
        with open(browser_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for entry in data:
            raw_timestamp = entry.get('timestamp')
            timestamp = None
            
            if raw_timestamp:
                try:
                    # Try parsing as UTC ISO format
                    if isinstance(raw_timestamp, str):
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
                    # Try parsing as Unix timestamp
                    elif isinstance(raw_timestamp, (int, float)):
                        dt = datetime.fromtimestamp(float(raw_timestamp), tz=timezone.utc)
                        timestamp = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                except Exception as e:
                    print(f"Browser log timestamp error: {str(e)} - Value: {raw_timestamp}")
                    timestamp = None
            
            event = {
                'timestamp': timestamp,
                'event_type': 'browser',
                'url': entry.get('data', {}).get('url'),
                'title': entry.get('data', {}).get('title'),
                'duration': entry.get('duration')
            }
            events.append(event)
        print(f"Parsed {len(events)} browser log events")
    except Exception as e:
        print(f"Error parsing browser log (skipping): {e}")
    return events


def parse_system_logs(sys_path):
    """Parse Kibana system JSON log (JSONL format)."""
    from datetime import datetime, timezone
    events = []
    parsed_lines = 0
    skipped_lines = 0
    
    try:
        with open(sys_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
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
                        # System logs should be in ISO format with Z
                        if isinstance(raw_timestamp, str):
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
                        print(f"System log timestamp error on line {line_num}: {str(e)}")
                        timestamp = None
                
                event = {
                    'timestamp': timestamp,
                    'event_type': 'system',
                    'process_name': log.get('process', {}).get('name'),
                    'command_line': log.get('process', {}).get('command_line'),
                    'log_level': log.get('log', {}).get('level'),
                    'message': log.get('message')
                }
                # Anonymize sensitive fields
                if log.get('host', {}).get('name'):
                    event['host_id'] = anonymize_id(log['host']['name'])
                if log.get('agent', {}).get('id'):
                    event['agent_id'] = anonymize_id(log['agent']['id'])
                    
                events.append(event)
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
        
        print(f"Parsed {len(events)} system log events from {parsed_lines} lines")
        if skipped_lines > 0:
            print(f"Skipped {skipped_lines} invalid/malformed lines")
    except Exception as e:
        print(f"Error parsing system log (skipping): {e}")
    return events


def parse_pcap_logs(pcap_path):
    """Parse PCAP file using tshark command (much faster than pyshark)."""
    from datetime import datetime
    events = []
    temp_json_path = None
    
    try:
        print("Converting PCAP to JSON using tshark...")
        
        # Create temporary JSON file
        temp_json = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        temp_json_path = temp_json.name
        temp_json.close()
        
        # Use tshark to convert PCAP to JSON
        tshark_cmd = [
            'tshark',
            '-r', pcap_path,
            '-T', 'json',
            '-e', 'frame.time_epoch',
            '-e', 'ip.src',
            '-e', 'ip.dst',
            '-e', 'frame.protocols',
            '-e', 'tcp.srcport',
            '-e', 'tcp.dstport',
            '-e', 'udp.srcport',
            '-e', 'udp.dstport',
            '-e', 'frame.len'
        ]
        
        # Run tshark and save output to temp file
        with open(temp_json_path, 'w') as f:
            result = subprocess.run(
                tshark_cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 minutes timeout
            )
        
        if result.returncode != 0:
            print(f"tshark error: {result.stderr}")
            return events
        
        print("Parsing JSON output...")
        
        # Read and parse the JSON
        with open(temp_json_path, 'r') as f:
            packets = json.load(f)
        
        # Convert to our event format
        for packet in packets:
            layers = packet.get('_source', {}).get('layers', {})
            
            raw_timestamp = layers.get('frame.time_epoch', [None])[0]
            timestamp = None
            
            if raw_timestamp:
                try:
                    # Network logs use Unix timestamps - convert to UTC
                    from datetime import timezone
                    dt = datetime.fromtimestamp(float(raw_timestamp), tz=timezone.utc)
                    timestamp = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                except Exception as e:
                    print(f"Network log timestamp error: {str(e)} - Value: {raw_timestamp}")
                    timestamp = None
            
            event = {
                'timestamp': timestamp,
                'event_type': 'network',
                'src_ip': layers.get('ip.src', [None])[0],
                'dst_ip': layers.get('ip.dst', [None])[0],
                'protocol': layers.get('frame.protocols', [None])[0],
                'src_port': layers.get('tcp.srcport', layers.get('udp.srcport', [None]))[0],
                'dst_port': layers.get('tcp.dstport', layers.get('udp.dstport', [None]))[0],
                'length': layers.get('frame.len', [None])[0]
            }
            
            # Convert port numbers to integers if present
            if event['src_port']:
                try:
                    event['src_port'] = int(event['src_port'])
                except:
                    pass
            if event['dst_port']:
                try:
                    event['dst_port'] = int(event['dst_port'])
                except:
                    pass
            if event['length']:
                try:
                    event['length'] = int(event['length'])
                except:
                    pass
            
            events.append(event)
        
        print(f"Parsed {len(events)} network packets")
        
    except FileNotFoundError:
        print("Error: tshark not found. Please install Wireshark (includes tshark)")
        print("Download from: https://www.wireshark.org/download.html")
    except subprocess.TimeoutExpired:
        print("Error: tshark processing timed out (file too large)")
    except Exception as e:
        print(f"Error parsing PCAP with tshark: {e}")
    finally:
        # Clean up temp file
        if temp_json_path and os.path.exists(temp_json_path):
            os.unlink(temp_json_path)
    
    return events


def remove_duplicates(events):
    """Identify exact duplicates while preserving event order and integrity."""
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
    from datetime import datetime, timezone
    
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
    
    print(f"\nTimestamp Standardization Results:")
    print(f"- Valid timestamps: {valid_count}")
    if problematic_events:
        print(f"- Events with timestamp issues: {len(problematic_events)}")
        print("\nSample problematic timestamps:")
        for evt in problematic_events[:3]:  # Show first 3 examples
            print(f"  - Value: {evt.get('timestamp')} | Error: {evt.get('timestamp_error')}")
    
    return events
