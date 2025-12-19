import json
import argparse
import os
import copy

def main():
    parser = argparse.ArgumentParser(description='Remove browser logs with empty title from JSON file.')
    parser.add_argument('file_path', help='Path to the JSON file')
    args = parser.parse_args()

    # Load the JSON data
    with open(args.file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Make a deep copy
    data = copy.deepcopy(data)

    # Filter the logs
    original_count = len(data['logs'])
    filtered_logs = []
    for log in data['logs']:
        # Remove only browser events with empty title or status 'not-afk' or status 'not-afk'
        if not (log.get('event_type') == 'browser' and 'data' in log and (log['data'].get('status') == 'not-afk' or log['data'].get('title') == '')):
            filtered_logs.append(log)

    # Update the data
    data['logs'] = filtered_logs
    filtered_count = len(filtered_logs)

    # Create new file path
    dir_path, filename = os.path.split(args.file_path)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_filtered{ext}"
    new_path = os.path.join(dir_path, new_filename)

    # Write to the new file
    with open(new_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Removed {original_count - filtered_count} logs (browser events with empty title)")
    print(f"Remaining logs: {filtered_count}")
    print(f"Filtered data saved to: {new_path}")

if __name__ == '__main__':
    main()