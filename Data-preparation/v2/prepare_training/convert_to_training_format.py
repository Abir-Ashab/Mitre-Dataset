"""
Convert balanced chunks to instruction-tuning format REFACTORED with SOLID principles.

Uses modular analyzers and formatters to generate field-specific training data.
Based on real attack patterns from documented penetration tests.
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from tqdm import tqdm

from config import (
    MERGED_CHUNKS_FILE,
    load_mitre_mapping,
    INSTRUCTION_TEMPLATE
)

# Import modular components
from models.analysis_result import AnalysisResult, EventAnalysis, SeverityLevel
from analyzers import ProcessAnalyzer, NetworkAnalyzer, FileAnalyzer
from formatters import SuspiciousFormatter, NormalFormatter
from rules import suspicious_patterns


# ============================================================================
# MODULAR ANALYSIS FUNCTIONS
# ============================================================================

def preprocess_log(log: Dict) -> Dict:
    """
    Flatten nested log structure to match analyzer expectations.
    
    Converts:
    - winlog.event_data.* -> top-level fields
    - winlog.event_id -> event_id/EventID
    - layers.IP.* and layers.TCP.* -> top-level fields
    
    Args:
        log: Original log with nested structure
        
    Returns:
        Flattened log dict
    """
    flat_log = log.copy()
    
    # Flatten winlog structure (system events)
    if 'winlog' in log:
        winlog = log['winlog']
        
        # Safety check: winlog should be a dict
        if not isinstance(winlog, dict):
            return flat_log
        
        # Copy event_id to top level
        if 'event_id' in winlog:
            flat_log['event_id'] = winlog['event_id']
            flat_log['EventID'] = winlog['event_id']
        
        # Flatten event_data fields
        if 'event_data' in winlog:
            event_data = winlog['event_data']
            # Check if event_data is a dict (sometimes it could be a list)
            if isinstance(event_data, dict):
                for key, value in event_data.items():
                    if key not in flat_log:  # Don't overwrite existing
                        flat_log[key] = value
    
    # Flatten network layers (network events)
    if 'layers' in log:
        layers = log['layers']
        
        # Safety check: layers should be a dict
        if not isinstance(layers, dict):
            return flat_log
        
        # Flatten IP layer
        if 'IP' in layers:
            ip_data = layers['IP']
            if isinstance(ip_data, dict):
                flat_log['SourceIp'] = ip_data.get('src', '')
                flat_log['SourceIP'] = ip_data.get('src', '')
                flat_log['DestinationIp'] = ip_data.get('dst', '')
                flat_log['DestIP'] = ip_data.get('dst', '')
                flat_log['DestinationAddress'] = ip_data.get('dst', '')
        
        # Flatten TCP layer
        if 'TCP' in layers:
            tcp_data = layers['TCP']
            if isinstance(tcp_data, dict):
                flat_log['SourcePort'] = tcp_data.get('sport', '')
                flat_log['DestinationPort'] = tcp_data.get('dport', '')
                flat_log['DestPort'] = tcp_data.get('dport', '')
                flat_log['tcp_flags'] = tcp_data.get('flags', '')
        
        # Add packet size from length field
        if 'length' in log:
            flat_log['packet_size'] = log['length']
    
    # Guess event_id for network events (they don't have one by default)
    if 'event_type' in log and log['event_type'] == 'network':
        if 'event_id' not in flat_log:
            flat_log['event_id'] = 3  # Sysmon network connection
            flat_log['EventID'] = 3
    elif 'event_type' in log and log['event_type'] == 'system':
        if 'event_id' not in flat_log and 'EventID' not in flat_log:
            # Try to infer from Image field
            if 'Image' in flat_log:
                flat_log['event_id'] = 1  # Sysmon process creation
                flat_log['EventID'] = 1
    
    return flat_log


def analyze_chunk(logs: List[Dict]) -> AnalysisResult:
    """
    Analyze chunk of logs using modular analyzers.
    
    Args:
        logs: List of log events
        
    Returns:
        AnalysisResult with all event analyses
    """
    # Initialize analyzers
    analyzers = [
        ProcessAnalyzer(),
        NetworkAnalyzer(),
        FileAnalyzer(),
    ]
    
    # Analyze each event
    event_analyses = []
    for log in logs:
        # Preprocess log to flatten nested structure
        flat_log = preprocess_log(log)
        
        # Find appropriate analyzer
        for analyzer in analyzers:
            if analyzer.can_analyze(flat_log):
                analysis = analyzer.analyze(flat_log)
                event_analyses.append(analysis)
                break
        # If no specialized analyzer, create basic analysis
        else:
            event_id = str(flat_log.get('event_id', flat_log.get('EventID', 'Unknown')))
            timestamp = flat_log.get('timestamp', flat_log.get('TimeCreated', ''))
            event_analyses.append(EventAnalysis(
                event_id=event_id,
                event_type='Generic',
                timestamp=timestamp,
                analysis_text=f"EventID {event_id} - standard system event",
                indicators=[],
                severity=SeverityLevel.LOW,
                field_references=[],
                mitre_techniques=[]
            ))
    
    # Detect attack chains
    attack_chain = detect_attack_chain(event_analyses)
    
    # Determine if suspicious
    is_suspicious = any(e.indicators for e in event_analyses)
    
    return AnalysisResult(
        is_suspicious=is_suspicious,
        event_analyses=event_analyses,
        metadata={'attack_chain': attack_chain}
    )


def detect_attack_chain(events: List[EventAnalysis]) -> str:
    """
    Detect attack chain patterns from event sequence.
    
    Args:
        events: List of analyzed events
        
    Returns:
        Attack chain name or empty string
    """
    # Get event types and check for patterns
    event_types = [e.event_type for e in events]
    all_techniques = []
    for e in events:
        all_techniques.extend(e.mitre_techniques)
    
    # Check against known attack chain patterns (it's a list of dicts)
    for pattern in suspicious_patterns.ATTACK_CHAIN_PATTERNS:
        chain_name = pattern['name']
        required_techniques = pattern.get('mitre_techniques', [])
        required_sequence = pattern.get('sequence', [])
        
        # Check if required techniques are present
        if all(tech in all_techniques for tech in required_techniques[:2]):  # At least 2 main techniques
            # Check if event sequence matches
            if all(event_type in event_types for event_type in required_sequence):
                return chain_name
    
    # Check for generic patterns
    if 'Process' in event_types and 'Network' in event_types:
        # Check for C2 indicators
        has_c2 = any('C2' in str(e.indicators) or 'T1071' in e.mitre_techniques for e in events)
        if has_c2:
            return 'c2_beacon_with_execution'
    
    if 'File' in event_types and len([e for e in events if e.event_type == 'File']) > 5:
        # Mass file operations
        has_ransomware = any('ransomware' in str(e.indicators).lower() or 'T1486' in e.mitre_techniques for e in events)
        if has_ransomware:
            return 'ransomware_chain'
    
    return ""


# ============================================================================
# TRAINING DATA GENERATION FUNCTIONS
# ============================================================================

def generate_suspicious_reason(logs: List[Dict], mitre_mapping: Dict) -> str:
    """
    Generate detailed, log-specific analysis for suspicious chunks using modular formatters.
    
    Args:
        logs: List of log events
        mitre_mapping: MITRE technique mapping (kept for compatibility)
        
    Returns:
        Detailed reason string with specific field references
    """
    # Analyze chunk using modular approach
    analysis = analyze_chunk(logs)
    
    # Format using SuspiciousFormatter
    formatter = SuspiciousFormatter()
    return formatter.format(analysis)


def generate_normal_reason(logs: List[Dict]) -> str:
    """
    Generate detailed, log-specific analysis for normal chunks using modular formatters.
    
    Args:
        logs: List of log events
        
    Returns:
        Detailed reason string explaining why logs are normal
    """
    # Analyze chunk using modular approach
    analysis = analyze_chunk(logs)
    
    # Format using NormalFormatter
    formatter = NormalFormatter()
    return formatter.format(analysis)


def create_training_example(chunk: Dict, mitre_mapping: Dict) -> Dict:
    """
    Convert a chunk to instruction-tuning format with SPECIFIC log analysis.
    
    Args:
        chunk: Chunk object with metadata and logs
        mitre_mapping: MITRE technique ID to name mapping
        
    Returns:
        Training example dict with instruction, input, output
    """
    # Handle case where chunk might be a list (shouldn't happen but let's check)
    if isinstance(chunk, list):
        raise ValueError(f"Chunk is a list with {len(chunk)} items, expected dict")
    
    metadata = chunk.get('metadata', {})
    logs = chunk.get('logs', [])
    chunk_label = chunk.get('chunk_label', 'unknown')
    
    # Prepare input logs (remove sensitive fields like label, mitre_techniques)
    input_logs = []
    for i, log in enumerate(logs):
        # Check if log is actually a dict
        if not isinstance(log, dict):
            raise ValueError(f"Log {i} is {type(log)}, expected dict. Log value: {str(log)[:200]}")
        
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
    
    # Generate SPECIFIC, LOG-AWARE output analysis
    if chunk_label == 'suspicious':
        output = generate_suspicious_reason(logs, mitre_mapping)
    else:
        output = generate_normal_reason(logs)
    
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
    error_details = []
    
    for i, chunk in enumerate(tqdm(chunks, desc="   Processing")):
        try:
            example = create_training_example(chunk, mitre_mapping)
            training_examples.append(example)
        except Exception as e:
            failed += 1
            if failed <= 3:  # Show first 3 errors with details
                error_info = f"Chunk {i}: {type(chunk).__name__}"
                if isinstance(chunk, dict):
                    error_info += f" with keys: {list(chunk.keys())}"
                elif isinstance(chunk, list):
                    error_info += f" with {len(chunk)} items, first item type: {type(chunk[0]).__name__ if chunk else 'empty'}"
                error_details.append(f"{error_info}\n      Error: {e}")
    
    if error_details:
        print("\n   ⚠️  Error Details:")
        for detail in error_details:
            print(f"      {detail}")
    
    if failed > 0:
        print(f"\n   ⚠️  {failed} chunks failed to convert")
    
    print(f"   ✅ Successfully converted {len(training_examples):,} examples")
    
    return training_examples


def main():
    """Main function to convert chunks to training format with IMPROVED QUALITY"""
    print("="*70)
    print("CONVERTING TO INSTRUCTION-TUNING FORMAT (IMPROVED)")
    print("="*70)
    print("🎯 New approach: Specific, log-aware analysis instead of templates")
    print("✅ Model will learn HOW to analyze, not just output format")
    print("="*70)
    
    # Load merged chunks
    print(f"\n📂 Loading: {MERGED_CHUNKS_FILE}")
    with open(MERGED_CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"   Loaded {len(chunks):,} chunks")
    
    # Convert to training format
    training_examples = convert_chunks_to_training_format(chunks)
    
    # Check if we have any examples
    if len(training_examples) == 0:
        print("\n" + "="*70)
        print("❌ CONVERSION FAILED - NO EXAMPLES GENERATED")
        print("="*70)
        print("All chunks failed to convert. Please check the error details above.")
        return []
    
    # Statistics
    suspicious_count = sum(1 for ex in training_examples if 'Suspicious' in ex['output'])
    normal_count = len(training_examples) - suspicious_count
    
    # Calculate output lengths to show improvement
    avg_output_len = sum(len(ex['output']) for ex in training_examples) / len(training_examples)
    
    print("\n" + "="*70)
    print("✅ CONVERSION COMPLETE (IMPROVED QUALITY)")
    print("="*70)
    print(f"Total examples: {len(training_examples):,}")
    print(f"Suspicious examples: {suspicious_count:,} ({suspicious_count/len(training_examples)*100:.1f}%)")
    print(f"Normal examples: {normal_count:,} ({normal_count/len(training_examples)*100:.1f}%)")
    print(f"\n📊 Quality Metrics:")
    print(f"   Average output length: {avg_output_len:.0f} characters")
    print(f"   (vs ~150 chars with old generic templates)")
    print(f"\n💡 Each example now contains:")
    print(f"   ✓ Specific field references (Process, CommandLine, DestIP, etc.)")
    print(f"   ✓ Explanation of WHY suspicious/normal")
    print(f"   ✓ Security context and indicators")
    print(f"   ✓ Unique analysis (not templates)")
    
    # Show sample outputs
    print(f"\n📋 Sample Training Output (Suspicious):")
    print("="*70)
    suspicious_example = next((ex for ex in training_examples if 'Suspicious' in ex['output']), None)
    if suspicious_example:
        print(suspicious_example['output'][:500] + "..." if len(suspicious_example['output']) > 500 else suspicious_example['output'])
    
    print(f"\n📋 Sample Training Output (Normal):")
    print("="*70)
    normal_example = next((ex for ex in training_examples if 'Normal' in ex['output']), None)
    if normal_example:
        print(normal_example['output'][:500] + "..." if len(normal_example['output']) > 500 else normal_example['output'])
    
    return training_examples


if __name__ == '__main__':
    main()
