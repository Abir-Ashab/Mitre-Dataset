import json
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data with robust encoding handling
def load_json_file(path):
    # Try UTF-8 first, then fallback to cp1252, using 'replace' to avoid decode errors
    encodings = [('utf-8', 'strict'), ('utf-8', 'replace'), ('cp1252', 'replace')]
    for enc, errors in encodings:
        try:
            with open(path, 'r', encoding=enc, errors=errors) as f:
                return json.load(f)
        except UnicodeDecodeError:
            # try next encoding
            continue
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
    print(f"Failed to read file with supported encodings: {path}")
    sys.exit(1)

data = load_json_file(filename)

# Set to store unique event IDs
unique_event_ids = set()

# Check if data has 'logs' key or is direct list
if 'logs' in data:
    logs = data['logs']
else:
    logs = data

# Iterate over the logs
for item in logs:
    if 'winlog' in item and 'event_id' in item['winlog']:
        unique_event_ids.add(item['winlog']['event_id'])

# Print the unique event IDs
print("Unique event IDs found:")
for eid in sorted(unique_event_ids):
    print(eid)