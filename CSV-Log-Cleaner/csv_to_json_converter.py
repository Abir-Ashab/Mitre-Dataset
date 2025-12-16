import csv
import json
from datetime import datetime

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

def convert_csv_to_json(csv_file, output_file):
    """
    Convert CSV log file to JSON format matching the syslog structure
    """
    result = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Build the JSON object matching syslog structure
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
            
            # Add entry to result
            result.append(log_entry)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in result:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"Converted {len(result)} log entries from {csv_file} to {output_file}")
    return len(result)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python csv_to_json_converter.py <csv_file> [output_file]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else csv_file.replace('.csv', '_converted.json')
    
    try:
        convert_csv_to_json(csv_file, output_file)
        print(f"Successfully created {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
