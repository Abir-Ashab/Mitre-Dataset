import json
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Load the JSON data with robust encoding handling
def load_json_file(path):
    encodings = [('utf-8', 'strict'), ('utf-8', 'replace'), ('cp1252', 'replace')]
    for enc, errors in encodings:
        try:
            with open(path, 'r', encoding=enc, errors=errors) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
    print(f"Failed to read file with supported encodings: {path}")
    sys.exit(1)

data = load_json_file(filename)

# Determine where the logs list lives
if isinstance(data, dict) and 'logs' in data and isinstance(data['logs'], list):
    logs = data['logs']
    container_type = 'dict'
elif isinstance(data, list):
    logs = data
    container_type = 'list'
else:
    print("No logs found in the provided file.")
    sys.exit(1)

# Filter out logs where Image matches the specified image path (case-insensitive and basename match)
remove_image_path = r"C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe"

def normalize_path(p):
    if not isinstance(p, str):
        return ''
    p = p.strip().strip('"')
    try:
        return os.path.normcase(os.path.normpath(p))
    except Exception:
        return p.lower()

target_norm = normalize_path(remove_image_path)
removed = 0
filtered_logs = []

for item in logs:
    image = None
    if isinstance(item, dict):
        image = item.get('winlog', {}).get('event_data', {}).get('Image')
    keep = True
    if image:
        normimg = normalize_path(image)
        if normimg == target_norm or os.path.basename(normimg) == os.path.basename(target_norm):
            keep = False
    if keep:
        filtered_logs.append(item)
    else:
        removed += 1

# Prepare new data structure for output
if container_type == 'dict':
    data['logs'] = filtered_logs
    new_data = data
else:
    new_data = filtered_logs

# Create new filename and write using UTF-8
base, ext = os.path.splitext(filename)
new_filename = base + "_filtered" + ext
with open(new_filename, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=2, ensure_ascii=False)

print(f"Processing complete. Filtered file saved as {new_filename}. Removed {removed} logs containing the image.")

print(f"Processing complete. Filtered file saved as {new_filename}. Removed logs with the specified Image.")