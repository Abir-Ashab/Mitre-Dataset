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
# Filter out logs where Image matches Chrome or VS Code
filtered_logs = []
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
vscode_path = "C:\\Users\\Niloy\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"

for item in data:
    if 'winlog' in item and 'event_data' in item['winlog'] and 'Image' in item['winlog']['event_data']:
        image = item['winlog']['event_data']['Image']
        if image != chrome_path and image != vscode_path:
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