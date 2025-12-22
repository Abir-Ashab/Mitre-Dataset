"""
Convert balanced chunks to instruction-tuning format
Creates the final training examples with instruction, input, and output
"""

import json
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

from config import (
    MERGED_CHUNKS_FILE,
    load_mitre_mapping,
    INSTRUCTION_TEMPLATE
)


def create_training_example(chunk: Dict, mitre_mapping: Dict) -> Dict:
    """
    Convert a chunk to instruction-tuning format
    
    Args:
        chunk: Chunk object with metadata and logs
        mitre_mapping: MITRE technique ID to name mapping
        
    Returns:
        Training example dict with instruction, input, output
    """
    metadata = chunk.get('metadata', {})
    logs = chunk.get('logs', [])
    chunk_label = chunk.get('chunk_label', 'unknown')
    
    # Prepare input logs (remove sensitive fields like label, mitre_techniques)
    input_logs = []
    for log in logs:
        # Remove fields that would give away the answer
        clean_log = {k: v for k, v in log.items() 
                    if k not in ['label', 'mitre_techniques', 'session_id', 'chunk_label']}
        input_logs.append(clean_log)
    
    # Create input structure
    input_data = {
        "metadata": {
            "session_id": metadata.get('session_id', 'unknown'),
            "chunk_index": metadata.get('chunk_index', 0),
            "start_time": metadata.get('start_time', 'unknown'),
            "end_time": metadata.get('end_time', 'unknown'),
            "number_of_events": len(input_logs)
        },
        "logs": input_logs
    }
    
    # Convert to JSON string for input
    input_text = json.dumps(input_data, ensure_ascii=False)
    
    # Create output based on chunk label
    if chunk_label == 'suspicious':
        # Collect all MITRE techniques from logs
        all_techniques = set()
        for log in logs:
            techniques = log.get('mitre_techniques', [])
            if techniques:
                all_techniques.update(techniques)
        
        output_parts = ["Status: Suspicious"]
        
        if all_techniques:
            # Format techniques with names
            formatted_techniques = []
            for technique in sorted(all_techniques):
                technique_name = mitre_mapping.get(technique, "Unknown Technique")
                formatted_techniques.append(f"{technique} ({technique_name})")
            
            output_parts.append(f"MITRE Techniques: {', '.join(formatted_techniques)}")
        else:
            output_parts.append("MITRE Techniques: Not specified")
        
        # Count suspicious logs
        suspicious_count = sum(1 for log in logs if log.get('label') == 'suspicious')
        output_parts.append(f"Reason: Malicious activity detected in {suspicious_count} out of {len(logs)} events based on behavioral patterns and attack signatures")
        
        output = "\n".join(output_parts)
    else:
        output = "Status: Normal\nReason: Standard system activity with no suspicious indicators across all events"
    
    return {
        "instruction": INSTRUCTION_TEMPLATE,
        "input": input_text,
        "output": output
    }


def convert_chunks_to_training_format(chunks: List[Dict]) -> List[Dict]:
    """
    Convert all chunks to training format
    
    Args:
        chunks: List of chunk objects
        
    Returns:
        List of training examples
    """
    print("\n🔄 Converting chunks to training format...")
    
    # Load MITRE mapping
    mitre_mapping = load_mitre_mapping()
    
    training_examples = []
    failed = 0
    
    for chunk in tqdm(chunks, desc="   Processing"):
        try:
            example = create_training_example(chunk, mitre_mapping)
            training_examples.append(example)
        except Exception as e:
            failed += 1
            if failed <= 5:  # Show first 5 errors
                print(f"\n   ⚠️  Error converting chunk: {e}")
    
    if failed > 0:
        print(f"\n   ⚠️  {failed} chunks failed to convert")
    
    print(f"   ✅ Successfully converted {len(training_examples):,} examples")
    
    return training_examples


def main():
    """Main function to convert chunks to training format"""
    print("="*70)
    print("CONVERTING TO INSTRUCTION-TUNING FORMAT")
    print("="*70)
    
    # Load merged chunks
    print(f"\n📂 Loading: {MERGED_CHUNKS_FILE}")
    with open(MERGED_CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"   Loaded {len(chunks):,} chunks")
    
    # Convert to training format
    training_examples = convert_chunks_to_training_format(chunks)
    
    # Statistics
    suspicious_count = sum(1 for ex in training_examples if 'Suspicious' in ex['output'])
    normal_count = len(training_examples) - suspicious_count
    
    print("\n" + "="*70)
    print("✅ CONVERSION COMPLETE")
    print("="*70)
    print(f"Total examples: {len(training_examples):,}")
    print(f"Suspicious examples: {suspicious_count:,} ({suspicious_count/len(training_examples)*100:.1f}%)")
    print(f"Normal examples: {normal_count:,} ({normal_count/len(training_examples)*100:.1f}%)")
    
    return training_examples


if __name__ == '__main__':
    main()
