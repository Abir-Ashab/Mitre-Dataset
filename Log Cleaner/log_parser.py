"""Log parsing functions for different log types."""
import json
import os
import hashlib


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
            
            # Preserve all data from the entry
            event = {
                'timestamp': timestamp,
                'event_type': 'browser'
            }
            # Add all fields from the entry, excluding timestamp if already processed
            for key, value in entry.items():
                if key != 'timestamp':
                    event[key] = value
            
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
    """Parse PCAP file using Scapy to preserve all packet data without loss."""
    try:
        import scapy.all as scapy
    except ImportError:
        print("Error: Scapy not installed. Install with: pip install scapy")
        return []
    
    from datetime import datetime, timezone
    events = []
    
    try:
        print("Reading PCAP file with Scapy...")
        packets = scapy.rdpcap(pcap_path)
        
        for i, pkt in enumerate(packets):
            raw_timestamp = float(pkt.time) if hasattr(pkt, 'time') else None
            timestamp = None
            
            if raw_timestamp:
                try:
                    dt = datetime.fromtimestamp(raw_timestamp, tz=timezone.utc)
                    timestamp = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                except Exception as e:
                    print(f"Network log timestamp error for packet {i+1}: {str(e)}")
                    timestamp = None
            
            # Preserve all packet data
            event = {
                'timestamp': timestamp,
                'event_type': 'network',
                'packet_number': i + 1,
                'length': len(pkt),
                'summary': pkt.summary(),
                'raw_hex': bytes(pkt).hex(),
                'layers': {}
            }
            
            # Extract information from each layer
            for layer in pkt.layers():
                layer_name = layer.__name__
                layer_data = {}
                if hasattr(pkt[layer], 'fields'):
                    for field_name, field_value in pkt[layer].fields.items():
                        if hasattr(field_value, '__str__'):
                            layer_data[field_name] = str(field_value)
                        else:
                            layer_data[field_name] = field_value
                event['layers'][layer_name] = layer_data
            
            events.append(event)
        
        print(f"Parsed {len(events)} network packets")
        
    except Exception as e:
        print(f"Error parsing PCAP with Scapy: {e}")
    
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
