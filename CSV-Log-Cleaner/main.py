"""
CSV Log Cleaner - Process logs from CSV-Logs folder
Handles CSV system logs, JSON browser logs, and PCAPNG network logs
"""
import json
import os
import csv
import copy
from datetime import datetime, timezone
import hashlib
import sys

try:
    import scapy.all as scapy
except ImportError:
    print("Error: scapy not installed. Run: pip install scapy")
    sys.exit(1)


def anonymize_id(value):
    """Anonymize machine-specific IDs by hashing."""
    if value:
        return hashlib.md5(value.encode()).hexdigest()[:8]
    return None


def extract_timestamp_from_csv_log(csv_path):
    """Extract timestamp from the first valid CSV log entry."""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamp_str = row.get('@timestamp', '')
                if timestamp_str:
                    try:
                        # Parse format like "Jul 9, 2025 @ 20:25:45.081"
                        dt = datetime.strptime(timestamp_str, "%b %d, %Y @ %H:%M:%S.%f")
                        return dt.strftime("%Y%m%d_%H%M%S")
                    except:
                        pass
        return None
    except Exception as e:
        print(f"Error extracting timestamp from CSV: {e}")
        return None


def parse_csv_system_logs(csv_path):
    """Parse CSV format system logs (from Kibana export) with full structure."""
    events = []
    parsed_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                parsed_count += 1
                timestamp_str = row.get('@timestamp', '')
                timestamp = None
                
                if timestamp_str:
                    try:
                        # Parse format like "Jul 9, 2025 @ 20:25:45.081"
                        dt = datetime.strptime(timestamp_str, "%b %d, %Y @ %H:%M:%S.%f")
                        # Convert to UTC ISO format
                        dt_utc = dt.replace(tzinfo=timezone.utc)
                        timestamp = dt_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                    except Exception as e:
                        print(f"Timestamp parse error: {e}")
                
                # Extract event data based on winlog fields
                event_data = {}
                for key, value in row.items():
                    if key and key.startswith('winlog.event_data.') and value:
                        field_name = key.replace('winlog.event_data.', '')
                        # Skip .keyword duplicates
                        if not field_name.endswith('.keyword'):
                            event_data[field_name] = value
                
                # Get event ID
                event_id = row.get('winlog.event_id', row.get('event.code', ''))
                
                # Only include if we have essential data
                if timestamp and event_id and event_data:
                    # Build full structure with blanks for missing fields
                    event = {
                        'timestamp': timestamp,
                        'event_type': 'system',
                        '@version': row.get('@version', '1'),
                        'event': {
                            'action': row.get('event.action', ''),
                            'created': row.get('event.created', ''),
                            'provider': row.get('event.provider', row.get('winlog.provider_name', '')),
                            'kind': row.get('event.kind', 'event'),
                            'original': row.get('event.original', row.get('message', '')),
                            'code': event_id
                        },
                        'tags': row.get('tags', '').split(',') if row.get('tags') else [],
                        'agent': {
                            'ephemeral_id': row.get('agent.ephemeral_id', ''),
                            'name': row.get('agent.name', row.get('host.name', '')),
                            'version': row.get('agent.version', ''),
                            'id': row.get('agent.id', ''),
                            'type': row.get('agent.type', '')
                        },
                        'log': {
                            'level': row.get('log.level', '')
                        },
                        'ecs': {
                            'version': row.get('ecs.version', '')
                        },
                        'message': row.get('message', row.get('event.original', '')),
                        'winlog': {
                            'provider_guid': row.get('winlog.provider_guid', ''),
                            'opcode': row.get('winlog.opcode', ''),
                            'channel': row.get('winlog.channel', ''),
                            'task': row.get('winlog.task', ''),
                            'computer_name': row.get('winlog.computer_name', row.get('host.name', '')),
                            'record_id': row.get('winlog.record_id', ''),
                            'event_data': event_data,
                            'event_id': event_id,
                            'provider_name': row.get('winlog.provider_name', ''),
                            'version': row.get('winlog.version', ''),
                            'user': {
                                'domain': row.get('winlog.user.domain', ''),
                                'name': row.get('winlog.user.name', ''),
                                'identifier': row.get('winlog.user.identifier', ''),
                                'type': row.get('winlog.user.type', '')
                            },
                            'process': {
                                'thread': {
                                    'id': row.get('winlog.process.thread.id', '')
                                },
                                'pid': row.get('winlog.process.pid', '')
                            }
                        },
                        'host': {
                            'name': row.get('host.name', '')
                        }
                    }
                    events.append(event)
        
        print(f"Parsed {len(events)} system log events from {parsed_count} CSV rows")
    except Exception as e:
        print(f"Error parsing CSV system log: {e}")
    
    return events


def parse_browser_logs(browser_path):
    """Parse ActivityWatch browser JSON log (bucket structure)."""
    events = []
    try:
        with open(browser_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle ActivityWatch export format - may have "buckets" wrapper or direct buckets
        buckets = data.get('buckets', data) if isinstance(data, dict) else {}
        
        if isinstance(buckets, dict):
            print(f"Found {len(buckets)} buckets in browser log")
            # Iterate through all buckets
            for bucket_name, bucket_data in buckets.items():
                if not isinstance(bucket_data, dict):
                    print(f"  Skipping {bucket_name}: not a dict")
                    continue
                if 'events' not in bucket_data:
                    print(f"  Skipping {bucket_name}: no events key")
                    continue
                
                bucket_events = bucket_data.get('events', [])
                print(f"  Processing {bucket_name}: {len(bucket_events)} events")
                for entry in bucket_events:
                    raw_timestamp = entry.get('timestamp')
                    timestamp = None
                    
                    if raw_timestamp:
                        try:
                            if isinstance(raw_timestamp, str):
                                if 'Z' in raw_timestamp:
                                    ts_str = raw_timestamp.replace('Z', '+00:00')
                                elif '+' not in raw_timestamp and '-' not in raw_timestamp[10:]:
                                    ts_str = raw_timestamp + '+00:00'
                                else:
                                    ts_str = raw_timestamp
                                dt = datetime.fromisoformat(ts_str)
                                dt_utc = dt.astimezone(timezone.utc)
                                timestamp = dt_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                            elif isinstance(raw_timestamp, (int, float)):
                                dt = datetime.fromtimestamp(float(raw_timestamp), tz=timezone.utc)
                                timestamp = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                        except Exception as e:
                            print(f"Browser timestamp error: {e}")
                    
                    event = {
                        'timestamp': timestamp,
                        'event_type': 'browser'
                    }
                    for key, value in entry.items():
                        if key != 'timestamp':
                            event[key] = value
                    
                    events.append(event)
        
        print(f"Parsed {len(events)} browser log events")
    except Exception as e:
        print(f"Error parsing browser log: {e}")
    
    return events


def parse_pcapng_network_logs(pcapng_path):
    """Parse PCAPNG network capture file with full layer details."""
    events = []
    
    try:
        packets = scapy.rdpcap(pcapng_path)
        print(f"Loaded {len(packets)} packets from PCAP")
        
        for idx, pkt in enumerate(packets):
            try:
                # Extract timestamp
                timestamp = None
                if hasattr(pkt, 'time'):
                    dt = datetime.fromtimestamp(float(pkt.time), tz=timezone.utc)
                    timestamp = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                
                # Build layers dictionary
                layers = {}
                
                # Ethernet layer
                if scapy.Ether in pkt:
                    ether = pkt[scapy.Ether]
                    layers['Ether'] = {
                        'dst': ether.dst,
                        'src': ether.src,
                        'type': str(ether.type)
                    }
                
                # IP layer
                if scapy.IP in pkt:
                    ip = pkt[scapy.IP]
                    layers['IP'] = {
                        'version': str(ip.version),
                        'ihl': str(ip.ihl),
                        'tos': str(ip.tos),
                        'len': str(ip.len),
                        'id': str(ip.id),
                        'flags': str(ip.flags),
                        'frag': str(ip.frag),
                        'ttl': str(ip.ttl),
                        'proto': str(ip.proto),
                        'chksum': str(ip.chksum),
                        'src': ip.src,
                        'dst': ip.dst,
                        'options': str(ip.options)
                    }
                
                # TCP layer
                if scapy.TCP in pkt:
                    tcp = pkt[scapy.TCP]
                    layers['TCP'] = {
                        'sport': str(tcp.sport),
                        'dport': str(tcp.dport),
                        'seq': str(tcp.seq),
                        'ack': str(tcp.ack),
                        'dataofs': str(tcp.dataofs),
                        'reserved': str(tcp.reserved),
                        'flags': str(tcp.flags),
                        'window': str(tcp.window),
                        'chksum': str(tcp.chksum),
                        'urgptr': str(tcp.urgptr),
                        'options': str(tcp.options)
                    }
                
                # UDP layer
                if scapy.UDP in pkt:
                    udp = pkt[scapy.UDP]
                    layers['UDP'] = {
                        'sport': str(udp.sport),
                        'dport': str(udp.dport),
                        'len': str(udp.len),
                        'chksum': str(udp.chksum)
                    }
                
                # Raw payload layer
                if scapy.Raw in pkt:
                    raw = pkt[scapy.Raw]
                    layers['Raw'] = {
                        'load': str(raw.load)
                    }
                
                # ICMP layer
                if scapy.ICMP in pkt:
                    icmp = pkt[scapy.ICMP]
                    layers['ICMP'] = {
                        'type': str(icmp.type),
                        'code': str(icmp.code),
                        'chksum': str(icmp.chksum)
                    }
                
                # Create event with full structure
                event = {
                    'timestamp': timestamp,
                    'event_type': 'network',
                    'packet_number': idx + 1,
                    'length': len(pkt),
                    'summary': pkt.summary(),
                    'raw_hex': '',  # Empty as in your example
                    'layers': layers
                }
                
                events.append(event)
            except KeyboardInterrupt:
                print(f"\nInterrupted by user at packet {idx+1}/{len(packets)}")
                raise
            except Exception as pkt_error:
                # Skip corrupted packets silently to avoid flooding output
                if idx % 10000 == 0 and idx > 0:
                    print(f"Processing packet {idx}/{len(packets)}...")
                continue
        
        print(f"Parsed {len(events)} network packets")
    except KeyboardInterrupt:
        print(f"\nPCAP parsing interrupted. Returning {len(events)} parsed packets so far.")
        return events
    except Exception as e:
        print(f"Error parsing PCAPNG: {e}")
    
    return events


def filter_system_log(event):
    """Remove unnecessary fields from system logs while preserving structure."""
    filtered = copy.deepcopy(event)
    
    # Remove all .keyword duplicate fields from winlog.event_data
    if 'winlog' in filtered and 'event_data' in filtered['winlog']:
        # Remove all .keyword fields (Elasticsearch duplicates)
        fields_to_remove = [key for key in filtered['winlog']['event_data'].keys() if key.endswith('.keyword')]
        for field in fields_to_remove:
            filtered['winlog']['event_data'].pop(field, None)
    
    # Don't remove any other fields - keep the full structure
    return filtered


def filter_network_log(event):
    """Remove unnecessary fields from network logs while preserving structure."""
    filtered = copy.deepcopy(event)
    
    # Remove infrastructure/metadata fields (not behavior traces)
    unnecessary_top_fields = [
        'packet_number',  # Sequential numbering, not temporal
        'raw_hex'  # Full packet bytes, too large for ML (kept empty in source)
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
    """Remove unnecessary fields from browser logs while preserving structure."""
    filtered = copy.deepcopy(event)
    
    # Keep id, duration, timestamp, event_type, and data fields
    # Only remove truly unnecessary fields from data
    if 'data' in filtered:
        unnecessary_data_fields = [
            'tabId', 'windowId', 'frameId',
            'transitionType', 'transitionQualifiers',
            'referrer'
        ]
        for field in unnecessary_data_fields:
            filtered['data'].pop(field, None)
    
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
        return copy.deepcopy(event)


def merge_and_clean_logs(system_events, network_events, browser_events, session_timestamp, host_id, agent_id):
    """Merge all log types and create final output structure."""
    all_logs = []
    
    # Add host_id and agent_id to each log
    for event in system_events:
        event['host_id'] = host_id
        event['agent_id'] = agent_id
        all_logs.append(event)
    
    for event in network_events:
        event['host_id'] = host_id
        event['agent_id'] = agent_id
        all_logs.append(event)
    
    for event in browser_events:
        event['host_id'] = host_id
        event['agent_id'] = agent_id
        all_logs.append(event)
    
    print(f"\nTotal events before filtering: {len(all_logs)}")
    
    # Sort by timestamp
    all_logs.sort(key=lambda x: x.get('timestamp', ''))
    
    # Apply field filtering to remove unnecessary fields
    print(f"\n=== Applying Field Filtering ===")
    filtered_logs = []
    removed_system_fields = 0
    removed_network_fields = 0
    removed_browser_fields = 0
    
    for event in all_logs:
        filtered_event = filter_log_entry(event)
        filtered_logs.append(filtered_event)
        
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
    
    print(f"Field filtering statistics:")
    print(f"  - System logs filtered: {removed_system_fields}")
    print(f"  - Network logs filtered: {removed_network_fields}")
    print(f"  - Browser logs filtered: {removed_browser_fields}")
    print(f"Total events after field filtering: {len(filtered_logs)}")
    
    return filtered_logs


def process_session_folder(folder_path, output_base_path):
    """Process a single session folder from CSV-Logs."""
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(folder_path)}")
    print(f"{'='*60}")
    
    # Find the log files (can have multiple CSVs)
    csv_logs = []
    browser_log = None
    pcapng_log = None
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.csv'):
            csv_logs.append(file_path)
        elif filename.endswith('.json'):
            browser_log = file_path
        elif filename.endswith('.pcapng') or filename.endswith('.pcap'):
            pcapng_log = file_path
    
    if not csv_logs or not browser_log or not pcapng_log:
        print(f"Warning: Missing log files in {folder_path}")
        print(f"  CSV: {len(csv_logs)} file(s)")
        print(f"  Browser: {browser_log is not None}")
        print(f"  Network: {pcapng_log is not None}")
        return None
    
    # Extract timestamp from first CSV log content
    session_timestamp = extract_timestamp_from_csv_log(csv_logs[0])
    if not session_timestamp:
        print(f"Error: Could not extract timestamp from CSV log")
        return None
    
    print(f"Session timestamp: {session_timestamp}")
    print(f"Found {len(csv_logs)} CSV system log file(s)")
    
    # Generate anonymized IDs
    host_id = anonymize_id(os.path.basename(folder_path))[:8]
    agent_id = anonymize_id(os.path.basename(folder_path) + "_agent")[:8]
    
    # Parse each log type
    print("\nParsing logs...")
    # Parse all CSV system logs and merge them
    system_events = []
    for csv_log in csv_logs:
        print(f"  Processing CSV: {os.path.basename(csv_log)}")
        events = parse_csv_system_logs(csv_log)
        system_events.extend(events)
    print(f"Total system events from all CSVs: {len(system_events)}")
    
    browser_events = parse_browser_logs(browser_log)
    network_events = parse_pcapng_network_logs(pcapng_log)
    
    # Merge and create output
    print("\nMerging logs...")
    output_data = merge_and_clean_logs(
        system_events, network_events, browser_events,
        session_timestamp, host_id, agent_id
    )
    
    # Create output directory with unique timestamp
    output_folder = os.path.join(output_base_path, session_timestamp)
    
    # Handle timestamp collision - append suffix if folder exists
    if os.path.exists(output_folder):
        suffix = 1
        while os.path.exists(f"{output_folder}_{suffix}"):
            suffix += 1
        original_timestamp = session_timestamp
        session_timestamp = f"{session_timestamp}_{suffix}"
        output_folder = os.path.join(output_base_path, session_timestamp)
        print(f"  Timestamp collision detected! Using: {session_timestamp}")
    
    os.makedirs(output_folder, exist_ok=True)
    
    # Write output file
    output_file = os.path.join(output_folder, f"text_log_{session_timestamp}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    total_logs = len(output_data)
    print(f"\n✓ Created: {output_file}")
    print(f"  Total logs: {total_logs}")
    print(f"  System: {len(system_events)}, Network: {len(network_events)}, Browser: {len(browser_events)}")
    
    return output_file


def main():
    """Main function to process all folders in CSV-Logs."""
    csv_logs_path = r"E:\Hacking\Mitre-Dataset\CSV-Logs"
    output_base_path = r"E:\Hacking\Mitre-Dataset\CSV-Logs-Cleaned"
    
    if not os.path.exists(csv_logs_path):
        print(f"Error: CSV-Logs folder not found at {csv_logs_path}")
        return
    
    # Create output directory
    os.makedirs(output_base_path, exist_ok=True)
    
    # Get all folders
    folders = [f for f in os.listdir(csv_logs_path) 
               if os.path.isdir(os.path.join(csv_logs_path, f))]
    
    print(f"Found {len(folders)} folders to process")
    
    processed = 0
    failed = 0
    
    for folder_name in sorted(folders):
        folder_path = os.path.join(csv_logs_path, folder_name)
        try:
            result = process_session_folder(folder_path, output_base_path)
            if result:
                processed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing {folder_name}: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total folders: {len(folders)}")
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")
    print(f"\nOutput location: {output_base_path}")


if __name__ == "__main__":
    main()
