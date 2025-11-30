import json
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data
with open(filename, 'r') as f:
    data = json.load(f)

# List to hold filtered logs
filtered_logs = []

# Iterate over the logs
if 'logs' in data:
    for item in data['logs']:
        if 'winlog' in item and 'event_id' in item['winlog']:
            if item['winlog']['event_id'] == "4624":
                filtered_logs.append(item)

# Create the sample_json file in the root
root_path = os.path.dirname(os.path.dirname(filename))  # Assuming filename is in Annotate-attack-logs/Pseudo-Annotated-Logs/...
sample_json_path = os.path.join(root_path, "sample_json.json")

# Write to the new file
with open(sample_json_path, 'w') as f:
    json.dump(filtered_logs, f, indent=2)

print(f"Sample JSON created at {sample_json_path} with {len(filtered_logs)} logs.")