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
                if ip_layer['src'] == "10.43.0.105" and ip_layer['dst'] == "150.171.27.12":
                    item['label'] = "suspicious"
                    item['mitre_techniques'] = ["T1105"]

# Create new filename
base, ext = os.path.splitext(filename)
new_filename = base + "_updated" + ext

# Write to new file
with open(new_filename, 'w') as f:
    json.dump(new_data, f, indent=2)

print(f"Processing complete. Updated file saved as {new_filename}")