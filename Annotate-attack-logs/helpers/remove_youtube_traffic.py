"""
Script to remove YouTube/Google network traffic from annotated log files.
Filters out network packets with YouTube/Google IP addresses.
"""
import os
import json
import shutil
from datetime import datetime


def is_youtube_ip(ip_address):
    """Check if an IP address belongs to YouTube/Google."""
    if not ip_address:
        return False
    
    # YouTube/Google IP ranges (based on actual traffic analysis)
    youtube_prefixes = [
        '74.125.',      # YouTube CDN (classic range)
        '142.250.',     # Google/YouTube (newer range) - 0.8% + 0.6% + 0.3% of traffic
        '142.251.',     # Google/YouTube (newer range) - 0.8% + 0.5% + 0.5% + 0.4% + 0.3% of traffic
    ]
    
    return any(ip_address.startswith(prefix) for prefix in youtube_prefixes)


def filter_youtube_from_logs(logs):
    """Remove YouTube network traffic from log entries."""
    filtered_logs = []
    youtube_count = 0
    
    for log_entry in logs:
        event_type = log_entry.get('event_type')
        
        # Only filter network events
        if event_type == 'network':
            layers = log_entry.get('layers', {})
            ip_layer = layers.get('IP', {})
            src_ip = ip_layer.get('src')
            dst_ip = ip_layer.get('dst')
            
            # Skip if either src or dst is a YouTube IP
            if is_youtube_ip(src_ip) or is_youtube_ip(dst_ip):
                youtube_count += 1
                continue
        
        filtered_logs.append(log_entry)
    
    return filtered_logs, youtube_count


def process_json_file(input_path, output_path):
    """
    Remove YouTube traffic from a single JSON file.
    
    Args:
        input_path: Path to the input JSON file
        output_path: Path to save the filtered JSON file
    
    Returns:
        Dictionary with statistics about the filtering process
    """
    print(f"\nProcessing: {os.path.basename(input_path)}")
    
    try:
        # Read the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get logs
        original_logs = data.get('logs', [])
        
        stats = {
            'total_logs': len(original_logs),
            'youtube_packets': 0,
            'filtered_logs': 0,
            'system_logs': 0,
            'network_logs': 0,
            'browser_logs': 0,
            'original_size_mb': 0,
            'filtered_size_mb': 0
        }
        
        # Count by type before filtering
        for log_entry in original_logs:
            event_type = log_entry.get('event_type')
            if event_type == 'system':
                stats['system_logs'] += 1
            elif event_type == 'network':
                stats['network_logs'] += 1
            elif event_type == 'browser':
                stats['browser_logs'] += 1
        
        # Filter YouTube traffic
        filtered_logs, youtube_count = filter_youtube_from_logs(original_logs)
        stats['youtube_packets'] = youtube_count
        stats['filtered_logs'] = len(filtered_logs)
        
        # Update data with filtered logs
        data['logs'] = filtered_logs
        
        # Calculate sizes
        original_size = os.path.getsize(input_path)
        stats['original_size_mb'] = round(original_size / (1024 * 1024), 2)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the filtered data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Calculate filtered size
        filtered_size = os.path.getsize(output_path)
        stats['filtered_size_mb'] = round(filtered_size / (1024 * 1024), 2)
        stats['reduction_percent'] = round(
            ((original_size - filtered_size) / original_size) * 100, 2
        )
        
        print(f"  Total logs: {stats['total_logs']}")
        print(f"    - System: {stats['system_logs']}")
        print(f"    - Network: {stats['network_logs']} (removed {stats['youtube_packets']} YouTube packets)")
        print(f"    - Browser: {stats['browser_logs']}")
        print(f"  Logs after filtering: {stats['filtered_logs']}")
        print(f"  Original size: {stats['original_size_mb']} MB")
        print(f"  Filtered size: {stats['filtered_size_mb']} MB")
        print(f"  Reduction: {stats['reduction_percent']}%")
        
        return stats
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def process_all_sessions(input_base_dir, output_base_dir):
    """
    Process all session folders to remove YouTube traffic.
    
    Args:
        input_base_dir: Base directory containing session folders
        output_base_dir: Base directory for filtered output
    """
    print("=" * 70)
    print("YouTube Traffic Removal Script")
    print("=" * 70)
    print(f"\nInput directory: {input_base_dir}")
    print(f"Output directory: {output_base_dir}")
    
    if not os.path.exists(input_base_dir):
        print(f"\nERROR: Input directory does not exist: {input_base_dir}")
        return
    
    # Get all session folders
    session_folders = [
        f for f in os.listdir(input_base_dir)
        if os.path.isdir(os.path.join(input_base_dir, f))
    ]
    
    if not session_folders:
        print("\nNo session folders found.")
        return
    
    print(f"\nFound {len(session_folders)} session folders")
    
    # Process each session folder
    overall_stats = {
        'processed': 0,
        'failed': 0,
        'total_youtube_packets': 0,
        'total_original_mb': 0,
        'total_filtered_mb': 0
    }
    
    for session_folder in sorted(session_folders):
        print(f"\n{'=' * 70}")
        print(f"Session: {session_folder}")
        print('=' * 70)
        
        input_session_dir = os.path.join(input_base_dir, session_folder)
        output_session_dir = os.path.join(output_base_dir, session_folder)
        
        # Find JSON files in the session folder
        json_files = [
            f for f in os.listdir(input_session_dir)
            if f.endswith('.json')
        ]
        
        if not json_files:
            print("No JSON files found in this session folder")
            continue
        
        # Process each JSON file
        for json_file in json_files:
            input_path = os.path.join(input_session_dir, json_file)
            
            # Create output filename with "_no_youtube" suffix
            base_name = os.path.splitext(json_file)[0]
            output_filename = f"{base_name}_no_youtube.json"
            output_path = os.path.join(output_session_dir, output_filename)
            
            stats = process_json_file(input_path, output_path)
            
            if stats:
                overall_stats['processed'] += 1
                overall_stats['total_youtube_packets'] += stats['youtube_packets']
                overall_stats['total_original_mb'] += stats['original_size_mb']
                overall_stats['total_filtered_mb'] += stats['filtered_size_mb']
            else:
                overall_stats['failed'] += 1
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print('=' * 70)
    print(f"Files processed successfully: {overall_stats['processed']}")
    print(f"Files failed: {overall_stats['failed']}")
    print(f"Total YouTube packets removed: {overall_stats['total_youtube_packets']}")
    print(f"Total original size: {round(overall_stats['total_original_mb'], 2)} MB")
    print(f"Total filtered size: {round(overall_stats['total_filtered_mb'], 2)} MB")
    
    if overall_stats['total_original_mb'] > 0:
        reduction = (
            (overall_stats['total_original_mb'] - overall_stats['total_filtered_mb'])
            / overall_stats['total_original_mb']
        ) * 100
        print(f"Overall reduction: {round(reduction, 2)}%")
        print(f"Space saved: {round(overall_stats['total_original_mb'] - overall_stats['total_filtered_mb'], 2)} MB")
    
    print(f"\nFiltered files saved to: {output_base_dir}")


def main():
    """Main entry point for the script."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python remove_youtube_traffic.py <input_json_file>")
        print("Example: python remove_youtube_traffic.py path/to/annotated_data.json")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"ERROR: File does not exist: {input_path}")
        sys.exit(1)
    
    if not input_path.endswith('.json'):
        print(f"ERROR: File must be a JSON file: {input_path}")
        sys.exit(1)
    
    # Create output path with "_no_youtube" suffix
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}_no_youtube.json"
    
    print("=" * 70)
    print("YouTube Traffic Removal Script")
    print("=" * 70)
    print(f"\nInput file: {input_path}")
    print(f"Output file: {output_path}")
    
    # Process the file
    stats = process_json_file(input_path, output_path)
    
    if stats:
        print("\n" + "=" * 70)
        print("YouTube Traffic Filtering Complete!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("Filtering Failed!")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()