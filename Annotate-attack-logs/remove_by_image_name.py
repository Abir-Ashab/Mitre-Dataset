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

# Assuming data is a list of log objects
# Filter out logs where Image matches
filtered_logs = []
for item in data:
    if 'winlog' in item and 'event_data' in item['winlog'] and 'Image' in item['winlog']['event_data']:
        if item['winlog']['event_data']['Image'] != "C:\\Program Files\\Wireshark\\extcap\\etwdump.exe":
            filtered_logs.append(item)
    else:
        filtered_logs.append(item)  # Keep if no Image field

new_data = filtered_logs

# Create new filename
base, ext = os.path.splitext(filename)
new_filename = base + "_filtered" + ext

# Write to new file
with open(new_filename, 'w') as f:
    json.dump(new_data, f, indent=2)

print(f"Processing complete. Filtered file saved as {new_filename}. Removed logs with the specified Image.")