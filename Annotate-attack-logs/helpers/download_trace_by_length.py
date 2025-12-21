import json
import sys
import os
import copy

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
                # if (ip_layer['src'] == "147.185.221.22" and # payload host site(playit-rclone upload) ip
                # if (ip_layer['src'] == "149.154.167.99" and # payload host site(tg) ip
                if (ip_layer['src'] == "31.216.145.5" and   # payload host site(mega) ip
                # if (ip_layer['src'] == "192.168.31.105" and   # local ip
                    ip_layer['dst'] == "192.168.31.105" and # local ip
                    # ip_layer['dst'] == "216.239.32.178" and   # gdrive ip
                    length_value > 500):
                    
                    item['label'] = "suspicious"
                    item['mitre_techniques'] = ["T1566.001", "T1105", "T1036", "T1027"] # normal c2 connection 
                    # item['mitre_techniques'] = ["T1071.001", "T1105", "T1048.003", "T1041"] # upload rclone.exe, rclone.conf
                    # item['mitre_techniques'] = ["T1567.002", "T1071.001"] # data exfiltration over cloud service
                    count += 1
                    
                    print(f"Marked as suspicious: timestamp={item.get('timestamp', 'N/A')}, "
                          f"length={length_value}, src={ip_layer['src']}, dst={ip_layer['dst']}")

# Create new filename
base, ext = os.path.splitext(filename)
new_filename = base + "_updated" + ext

# Write to new file
with open(new_filename, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=2, ensure_ascii=False)

print(f"\nProcessing complete!")
print(f"Total entries marked as suspicious: {count}")
print(f"Updated file saved as: {new_filename}")

# python .\download_trace_by_length.py "E:\Hacking\Mitre-Dataset\Annotate-attack-logs\Pseudo-Annotated-Logs\20250629_200301\annotated_data_20250629_200301_updated.json"