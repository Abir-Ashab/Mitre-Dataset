import os
import json

def clean_dict(d):
    if isinstance(d, dict):
        keys_to_remove = []
        for k, v in d.items():
            if v == "-":
                keys_to_remove.append(k)
            else:
                clean_dict(v)
        for k in keys_to_remove:
            del d[k]
    elif isinstance(d, list):
        for item in d:
            clean_dict(item)

def clean_json_files(root_path):
    for folder in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith('.json'):
                    file_path = os.path.join(folder_path, file)
                    print(f"Processing {file_path}")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        clean_dict(data)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=4)
                        
                        print(f"Cleaned {file_path}")
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    root_path = r"E:\Hacking\Mitre-Dataset\Annotate-attack-logs\Pseudo-Annotated-Logs"
    clean_json_files(root_path)