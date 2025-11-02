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
    events = []
    try:
        with open(browser_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for entry in data:
            event = {
                'timestamp': entry.get('timestamp'),
                'event_type': 'browser',
                'url': entry.get('data', {}).get('url'),
                'title': entry.get('data', {}).get('title'),
                'duration': entry.get('duration')
            }
            events.append(event)
        print(f"Parsed {len(events)} browser log events")
    except Exception as e:
        print(f"Error parsing browser log: {e}")
    return events


def parse_system_logs(sys_path):
    """Parse Kibana system JSON log (JSONL format)."""
    events = []
    try:
        with open(sys_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            if not line.strip():
                continue
            try:
                log = json.loads(line)
                event = {
                    'timestamp': log.get('@timestamp'),
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
            except json.JSONDecodeError:
                continue
        print(f"Parsed {len(events)} system log events")
    except Exception as e:
        print(f"Error parsing system log: {e}")
    return events


def parse_pcap_logs(pcap_path):
    """Parse PCAP file using tshark command (much faster than pyshark)."""
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
            
            event = {
                'timestamp': layers.get('frame.time_epoch', [None])[0],
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
    """Keep all events - no deduplication."""
    print(f"Keeping all {len(events)} events (deduplication disabled)")
    return events


def standardize_timestamps(events):
    """Ensure timestamps are in consistent string format."""
    for event in events:
        timestamp = event.get('timestamp')
        if timestamp and not isinstance(timestamp, str):
            try:
                event['timestamp'] = timestamp.isoformat()
            except:
                event['timestamp'] = str(timestamp)
    return events
