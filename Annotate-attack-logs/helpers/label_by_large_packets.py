import json
import sys
import os
import copy

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data
with open(filename, 'r') as f:
    data = json.load(f)

# Make a deep copy
new_data = copy.deepcopy(data)

# Counter for tracking changes
count = 0

# Iterate over the logs
if 'logs' in new_data:
    for item in new_data['logs']:
        # Check if the necessary fields exist
        if 'layers' in item and 'IP' in item['layers'] and 'length' in item:
            ip_layer = item['layers']['IP']
            
            # Check src, dst, and length conditions
            if 'src' in ip_layer and 'dst' in ip_layer:
                # Convert length to int if it's a string
                length_value = int(item['length']) if isinstance(item['length'], str) else item['length']
                
                # Check the conditions: src, dst, and length > 500
                if (ip_layer['src'] == "31.216.145.5" and 
                    ip_layer['dst'] == "10.100.200.151" and 
                    length_value > 500):
                    
                    item['label'] = "suspicious"
                    item['mitre_techniques'] = ["T1566.001", "T1105", "T1036", "T1027"]
                    count += 1
                    
                    print(f"Marked as suspicious: timestamp={item.get('timestamp', 'N/A')}, "
                          f"length={length_value}, src={ip_layer['src']}, dst={ip_layer['dst']}")

# Create new filename
base, ext = os.path.splitext(filename)
new_filename = base + "_updated" + ext

# Write to new file
with open(new_filename, 'w') as f:
    json.dump(new_data, f, indent=2)

print(f"\nProcessing complete!")
print(f"Total entries marked as suspicious: {count}")
print(f"Updated file saved as: {new_filename}")

# python .\detect_large_packets.py E:\Hacking\Mitre-Dataset\Annotate-attack-logs\Pseudo-Annotated-Logs\20251025_142600\annotated_data_20251025_142600.json