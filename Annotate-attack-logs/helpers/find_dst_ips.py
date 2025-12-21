import json
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data by trying several encodings and a safe fallback

def load_json_file(path):
    encodings = ('utf-8', 'utf-8-sig', 'latin-1', 'cp1252')
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            # try the next encoding
            continue
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON (encoding={enc}): {e}")
            sys.exit(1)
    # Last resort: replace undecodable bytes and attempt to load
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            print("Warning: some invalid bytes were replaced when decoding the file.")
            return json.load(f)
    except Exception as e:
        print(f"Could not read or parse the file with tried encodings: {e}")
        sys.exit(1)


data = load_json_file(filename)

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