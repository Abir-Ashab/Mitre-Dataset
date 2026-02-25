import json
import re
import os

def remove_labels_from_chunk(chunk):
    """
    Remove label and mitre_techniques fields from all logs in a chunk to create proper test data.
    The model should predict these fields, not receive them as input.
    Returns: (clean_chunk, ground_truth) where ground_truth contains the removed data for verification
    """
    clean_chunk = chunk.copy()
    ground_truth = {
        'label': None,
        'mitre_techniques': []
    }
    
    if 'logs' in clean_chunk:
        clean_chunk['logs'] = []
        for log in chunk['logs']:
            clean_log = log.copy()
            
            # Extract ground truth before removing
            if 'label' in clean_log and ground_truth['label'] is None:
                ground_truth['label'] = clean_log['label']
            if 'mitre_techniques' in clean_log and len(clean_log.get('mitre_techniques', [])) > 0:
                ground_truth['mitre_techniques'].extend(clean_log['mitre_techniques'])
            
            # Remove the fields
            if 'label' in clean_log:
                del clean_log['label']
            if 'mitre_techniques' in clean_log:
                del clean_log['mitre_techniques']
                
            clean_chunk['logs'].append(clean_log)
    
    # Deduplicate MITRE techniques
    ground_truth['mitre_techniques'] = list(set(ground_truth['mitre_techniques']))
    
    return clean_chunk, ground_truth

def extract_chunks_by_type(file_path, n_system=20, n_network=10):
    """
    Extract chunks from a JSON array file, categorized by log type.
    Returns two lists: system_chunks and network_chunks
    Labels are removed from individual logs to create proper test data.
    """
    system_chunks = []
    network_chunks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Skip opening bracket
        f.readline()
        
        bracket_count = 0
        current_item = []
        
        for line in f:
            current_item.append(line)
            
            # Count brackets to detect complete objects
            bracket_count += line.count('{') - line.count('}')
            
            # When bracket_count returns to 0, we have a complete object
            if bracket_count == 0 and len(current_item) > 1:
                # Join the lines and parse
                item_str = ''.join(current_item).strip()
                # Remove trailing comma if present
                if item_str.endswith(','):
                    item_str = item_str[:-1]
                
                try:
                    item = json.loads(item_str)
                    
                    # Determine if this chunk is primarily system or network logs
                    if 'logs' in item and len(item['logs']) > 0:
                        # Count event types in the chunk
                        system_count = sum(1 for log in item['logs'] if log.get('event_type') == 'system')
                        network_count = sum(1 for log in item['logs'] if log.get('event_type') == 'network')
                        
                        # Remove labels from the chunk and extract ground truth
                        clean_chunk, ground_truth = remove_labels_from_chunk(item)
                        
                        # Categorize based on majority type
                        if system_count >= network_count:
                            if len(system_chunks) < n_system:
                                system_chunks.append((clean_chunk, ground_truth))
                        else:
                            if len(network_chunks) < n_network:
                                network_chunks.append((clean_chunk, ground_truth))
                    
                    current_item = []
                    
                    # Stop if we have enough of both types
                    if len(system_chunks) >= n_system and len(network_chunks) >= n_network:
                        break
                        
                except json.JSONDecodeError:
                    current_item = []
                    bracket_count = 0
    
    return system_chunks, network_chunks

# Create data directory if it doesn't exist
data_dir = 'E:/Hacking/Mitre-Dataset/mitre-attack-analyzer/data'
os.makedirs(data_dir, exist_ok=True)

# Clear old files
print('Cleaning old test files...')
for file in os.listdir(data_dir):
    if file.startswith('test_') and file.endswith('.json'):
        os.remove(os.path.join(data_dir, file))
        print(f'  Removed {file}')

# Extract normal chunks (20 system, 10 network)
print('\nExtracting normal chunks...')
normal_system, normal_network = extract_chunks_by_type(
    'E:/Hacking/Mitre-Dataset/Data-preparation/v2/training_data/normal_chunks.json',
    n_system=20,
    n_network=10
)

# Save normal system chunks
answer_key = {}
print(f'\nSaving {len(normal_system)} normal system chunks...')
for i, (chunk, ground_truth) in enumerate(normal_system):
    file_name = f'test_normal_system_{i}.json'
    file_path = f'{data_dir}/{file_name}'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)
    answer_key[file_name] = ground_truth
    print(f'  ✓ {file_name}')

# Save normal network chunks
print(f'\nSaving {len(normal_network)} normal network chunks...')
for i, (chunk, ground_truth) in enumerate(normal_network):
    file_name = f'test_normal_network_{i}.json'
    file_path = f'{data_dir}/{file_name}'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)
    answer_key[file_name] = ground_truth
    print(f'  ✓ {file_name}')

# Extract suspicious chunks (20 system, 10 network)
print('\nExtracting suspicious chunks...')
suspicious_system, suspicious_network = extract_chunks_by_type(
    'E:/Hacking/Mitre-Dataset/Data-preparation/v2/training_data/suspicious_chunks.json',
    n_system=20,
    n_network=10
)

# Save suspicious system chunks
print(f'\nSaving {len(suspicious_system)} suspicious system chunks...')
for i, (chunk, ground_truth) in enumerate(suspicious_system):
    file_name = f'test_suspicious_system_{i}.json'
    file_path = f'{data_dir}/{file_name}'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)
    answer_key[file_name] = ground_truth
    print(f'  ✓ {file_name}')

# Save suspicious network chunks
print(f'\nSaving {len(suspicious_network)} suspicious network chunks...')
for i, (chunk, ground_truth) in enumerate(suspicious_network):
    file_name = f'test_suspicious_network_{i}.json'
    file_path = f'{data_dir}/{file_name}'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)
    answer_key[file_name] = ground_truth
    print(f'  ✓ {file_name}')

print(f'\n✅ Done!')
print(f'\nSummary:')
print(f'  Normal:     {len(normal_system)} system + {len(normal_network)} network = {len(normal_system) + len(normal_network)} total')
print(f'  Suspicious: {len(suspicious_system)} system + {len(suspicious_network)} network = {len(suspicious_system) + len(suspicious_network)} total')
print(f'  Grand total: {len(normal_system) + len(normal_network) + len(suspicious_system) + len(suspicious_network)} files')
print(f'\nAll files saved to: mitre-attack-analyzer/data/')

# Save answer key with labels and MITRE techniques
answer_key_path = f'{data_dir}/answer_key.json'
with open(answer_key_path, 'w', encoding='utf-8') as f:
    json.dump(answer_key, f, indent=2, ensure_ascii=False)

print(f'\n📋 Answer key created: mitre-attack-analyzer/data/answer_key.json')
print(f'   (Contains true labels and MITRE techniques for each test file)')


