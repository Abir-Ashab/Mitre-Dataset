import json
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data
try:
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    print(f"Error at line {e.lineno}, column {e.colno}")
    print(f"Error message: {e.msg}")
    sys.exit(1)
except Exception as e:
    print(f"Error loading file: {e}")
    sys.exit(1)

# Assuming data is an object with "logs" array
# Make a deep copy
import copy
new_data = copy.deepcopy(data)

# Iterate over the logs
if 'logs' in new_data:
    for item in new_data['logs']:
        if 'layers' in item and 'IP' in item['layers']:
            ip_layer = item['layers']['IP']
            if 'src' in ip_layer and 'dst' in ip_layer:
                # if ip_layer['src'] == "192.168.31.105" and ip_layer['dst'] == "147.185.221.22":
                if ip_layer['src'] == "147.185.221.22" and ip_layer['dst'] == "192.168.31.105":
                    item['label'] = "suspicious"
                    item['mitre_techniques'] = ["T1571", "T1071.001", "T1090", "T1572"]

# Create new filename
base, ext = os.path.splitext(filename)
new_filename = base + "_updated" + ext

# Write to new file
with open(new_filename, 'w') as f:
    json.dump(new_data, f, indent=2)

print(f"Processing complete. Updated file saved as {new_filename}")