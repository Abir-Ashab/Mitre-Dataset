import json
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data
with open(filename, 'r') as f:
    data = json.load(f)

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