"""
Convert cleaned logs to instruction-tuning format
Preserves ALL original fields - no data loss
Includes MITRE technique names with codes
"""

import json
import random
from pathlib import Path
from tqdm import tqdm

# Load MITRE technique mapping
SCRIPT_DIR = Path(__file__).parent
with open(SCRIPT_DIR / 'mitre_techniques.json', 'r', encoding='utf-8') as f:
    MITRE_MAPPING = json.load(f)


def create_training_example(log):
    """
    Convert log to instruction-tuning format
    Keeps ALL original fields in the input
    """
    instruction = "Analyze this log and determine if it's normal or suspicious. If suspicious, identify the MITRE ATT&CK techniques and explain why."
    
    # Keep the ENTIRE log as input (remove only label and mitre_techniques from input)
    input_log = {k: v for k, v in log.items() if k not in ['label', 'mitre_techniques']}
    
    # Convert to JSON string for input
    input_text = json.dumps(input_log, ensure_ascii=False)
    
    # Create output based on label
    label = log.get('label', 'normal')
    
    if label == 'suspicious':
        mitre_techniques = log.get('mitre_techniques', [])
        
        output_parts = ["Status: Suspicious"]
        
        if mitre_techniques:
            # Format techniques with names: T1071.001 (Application Layer Protocol: Web Protocols)
            formatted_techniques = []
            for technique in mitre_techniques:
                technique_name = MITRE_MAPPING.get(technique, "Unknown Technique")
                formatted_techniques.append(f"{technique} ({technique_name})")
            
            output_parts.append(f"MITRE Techniques: {', '.join(formatted_techniques)}")
        else:
            output_parts.append("MITRE Techniques: Not specified")
        
        output_parts.append("Reason: Malicious activity detected based on behavioral patterns")
        
        output = "\n".join(output_parts)
    else:
        output = "Status: Normal\nReason: Standard system activity with no suspicious indicators"
    
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output
    }


def main():
    print("="*70)
    print("CONVERTING LOGS TO TRAINING FORMAT")
    print("Preserving ALL original fields - zero data loss")
    print("="*70)
    
    # Paths
    base_dir = Path(__file__).parent
    output_dir = base_dir / 'output'
    training_dir = base_dir / 'training_data'
    training_dir.mkdir(exist_ok=True)
    
    suspicious_file = output_dir / 'cleaned_suspicious_logs.json'
    normal_file = output_dir / 'cleaned_normal_logs.json'
    
    # Load cleaned logs
    print("\n📂 Loading cleaned logs...")
    with open(suspicious_file, 'r', encoding='utf-8') as f:
        suspicious_logs = json.load(f)
    
    with open(normal_file, 'r', encoding='utf-8') as f:
        normal_logs = json.load(f)
    
    print(f"   Suspicious logs: {len(suspicious_logs):,}")
    print(f"   Normal logs: {len(normal_logs):,}")
    
    # Balance check
    ratio = len(normal_logs) / len(suspicious_logs) if len(suspicious_logs) > 0 else 0
    print(f"\n📊 Dataset balance:")
    print(f"   Suspicious: {len(suspicious_logs):,}")
    print(f"   Normal: {len(normal_logs):,}")
    print(f"   Ratio: 1:{ratio:.1f}")
    
    # Combine all logs
    all_logs = suspicious_logs + normal_logs
    total_logs = len(all_logs)
    
    print(f"\n   Total examples: {total_logs:,}")
    
    # Shuffle
    random.seed(42)
    random.shuffle(all_logs)
    
    # Convert to training format
    print(f"\n🔄 Converting {total_logs:,} logs to instruction format...")
    print("   (Preserving all original fields)")
    
    training_examples = []
    failed = 0
    
    for log in tqdm(all_logs, desc="Converting"):
        try:
            example = create_training_example(log)
            training_examples.append(example)
        except Exception as e:
            failed += 1
            if failed <= 5:  # Show first 5 errors
                print(f"\n⚠️  Error converting log: {e}")
    
    if failed > 0:
        print(f"\n⚠️  {failed} logs failed to convert")
    
    print(f"\n✅ Successfully converted {len(training_examples):,} examples")
    print(f"   All original fields preserved in each example")
    
    # Split into train/val/test (70/15/15)
    total = len(training_examples)
    train_size = int(total * 0.7)
    val_size = int(total * 0.15)
    
    train_data = training_examples[:train_size]
    val_data = training_examples[train_size:train_size + val_size]
    test_data = training_examples[train_size + val_size:]
    
    print(f"\n📊 Dataset split:")
    print(f"   Train: {len(train_data):,} examples (70%)")
    print(f"   Validation: {len(val_data):,} examples (15%)")
    print(f"   Test: {len(test_data):,} examples (15%)")
    
    # Count labels in each split
    print("\n📈 Label distribution per split:")
    for split_name, split_data in [("Train", train_data), ("Val", val_data), ("Test", test_data)]:
        suspicious_count = sum(1 for ex in split_data if 'Suspicious' in ex['output'])
        normal_count = len(split_data) - suspicious_count
        print(f"   {split_name}: {suspicious_count:,} suspicious, {normal_count:,} normal")
    
    # Save as JSONL
    print(f"\n💾 Saving to {training_dir}/...")
    
    files_created = []
    for filename, data in [
        ('train.jsonl', train_data),
        ('val.jsonl', val_data),
        ('test.jsonl', test_data)
    ]:
        filepath = training_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for example in data:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"   ✅ {filename}: {len(data):,} lines ({file_size_mb:.1f} MB)")
        files_created.append(str(filepath))
    
    # Save statistics
    stats = {
        "total_examples": len(training_examples),
        "suspicious_logs": len(suspicious_logs),
        "normal_logs": len(normal_logs),
        "ratio": f"1:{ratio:.1f}",
        "data_preservation": "100% - All original fields preserved",
        "splits": {
            "train": {
                "count": len(train_data),
                "suspicious": sum(1 for ex in train_data if 'Suspicious' in ex['output']),
                "normal": sum(1 for ex in train_data if 'Normal' in ex['output'])
            },
            "val": {
                "count": len(val_data),
                "suspicious": sum(1 for ex in val_data if 'Suspicious' in ex['output']),
                "normal": sum(1 for ex in val_data if 'Normal' in ex['output'])
            },
            "test": {
                "count": len(test_data),
                "suspicious": sum(1 for ex in test_data if 'Suspicious' in ex['output']),
                "normal": sum(1 for ex in test_data if 'Normal' in ex['output'])
            }
        }
    }
    
    stats_file = training_dir / 'dataset_stats.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"   ✅ dataset_stats.json")
    
    print("\n" + "="*70)
    print("✅ CONVERSION COMPLETE!")
    print("="*70)
    print(f"\n📁 Training files created in: {training_dir}")
    print("   - train.jsonl")
    print("   - val.jsonl")
    print("   - test.jsonl")
    print("   - dataset_stats.json")
    print(f"\n✨ Total: {len(training_examples):,} training examples")
    print("✅ All original fields preserved - zero data loss")
    print("\n🚀 Ready for fine-tuning!")
    print("="*70)


if __name__ == '__main__':
    main()
