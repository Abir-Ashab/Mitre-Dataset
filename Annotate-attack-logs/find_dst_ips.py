import json
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data
with open(filename, 'r') as f:
    data = json.load(f)

# Set to store unique dst IPs
unique_dst_ips = set()

# Iterate over the logs
if 'logs' in data:
    for item in data['logs']:
        if 'layers' in item and 'IP' in item['layers']:
            ip_layer = item['layers']['IP']
            if 'dst' in ip_layer:
                unique_dst_ips.add(ip_layer['dst'])

# Print the unique dst IPs
print("Unique destination IPs found:")
for ip in sorted(unique_dst_ips):
    print(ip)