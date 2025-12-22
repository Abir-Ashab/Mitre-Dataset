"""
Extract logs by label (suspicious/normal) from annotated data
Usage: python extract_logs.py --label suspicious
       python extract_logs.py --label normal
"""

import json
import argparse
from pathlib import Path
from tqdm import tqdm


def extract_logs_by_label(annotated_logs_dir, label_type, output_file):
    """
    Extract all logs with specified label from annotated sessions
    
    Args:
        annotated_logs_dir: Path to Annotated-Logs directory
        label_type: 'suspicious' or 'normal'
        output_file: Path to save extracted logs
    """
    annotated_logs_dir = Path(annotated_logs_dir)
    
    # Get all session folders
    session_folders = sorted([f for f in annotated_logs_dir.iterdir() if f.is_dir()])
    
    print(f"Found {len(session_folders)} session folders")
    print(f"Extracting logs with label: {label_type}")
    print("-" * 60)
    
    extracted_logs = []
    session_stats = {}
    
    # Process each session
    for folder in tqdm(session_folders, desc="Processing sessions"):
        json_files = list(folder.glob("*.json"))
        
        if not json_files:
            print(f"⚠️  No JSON file in {folder.name}")
            continue
        
        try:
            with open(json_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session_id = data.get('session_id', folder.name)
            session_count = 0
            
            # Extract logs with matching label
            for log in data.get('logs', []):
                if log.get('label') == label_type:
                    # Add session_id to each log for tracking
                    log['session_id'] = session_id
                    extracted_logs.append(log)
                    session_count += 1
            
            session_stats[session_id] = session_count
            
        except Exception as e:
            print(f"❌ Error processing {folder.name}: {e}")
    
    # Save extracted logs
    output_file = Path(output_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_logs, f, indent=2)
    
    # Print statistics
    print("\n" + "=" * 60)
    print(f"✅ EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Total {label_type} logs extracted: {len(extracted_logs):,}")
    print(f"Saved to: {output_file}")
    print("\n📊 Logs per session:")
    for session_id, count in sorted(session_stats.items()):
        if count > 0:
            print(f"   {session_id}: {count:,}")
    print("=" * 60)
    
    return extracted_logs, session_stats


def main():
    parser = argparse.ArgumentParser(description='Extract logs by label from annotated data')
    parser.add_argument(
        '--label',
        type=str,
        required=True,
        choices=['suspicious', 'normal'],
        help='Label type to extract: suspicious or normal'
    )
    parser.add_argument(
        '--input',
        type=str,
        default=r'E:\Hacking\Mitre-Dataset\Annotate-attack-logs\Annotated-Logs',
        help='Path to Annotated-Logs directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: extracted_{label}_logs.json)'
    )
    
    args = parser.parse_args()
    
    # Set default output file if not specified
    if args.output is None:
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)
        args.output = output_dir / f'extracted_{args.label}_logs.json'
    
    # Extract logs
    extract_logs_by_label(args.input, args.label, args.output)


if __name__ == '__main__':
    main()
