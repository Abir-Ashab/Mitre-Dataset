"""
Configuration for training data preparation
"""

from pathlib import Path
import json

# Base paths
BASE_DIR = Path(__file__).parent
V2_DIR = BASE_DIR.parent
TRAINING_DATA_DIR = V2_DIR / 'training_data'

# Input files (chunks from previous pipeline)
SUSPICIOUS_CHUNKS_FILE = TRAINING_DATA_DIR / 'suspicious_chunks.json'
NORMAL_CHUNKS_FILE = TRAINING_DATA_DIR / 'normal_chunks.json'

# Output directory for final training data
FINAL_OUTPUT_DIR = BASE_DIR / 'final_training_data'
FINAL_OUTPUT_DIR.mkdir(exist_ok=True)

# Intermediate files
MERGED_CHUNKS_FILE = BASE_DIR / 'merged_balanced_chunks.json'

# Final training files (JSONL format)
TRAIN_FILE = FINAL_OUTPUT_DIR / 'train.jsonl'
VAL_FILE = FINAL_OUTPUT_DIR / 'val.jsonl'
TEST_FILE = FINAL_OUTPUT_DIR / 'test.jsonl'

# MITRE techniques mapping
MITRE_MAPPING_FILE = V2_DIR / 'mitre_techniques.json'

# Load MITRE mapping
def load_mitre_mapping():
    """Load MITRE technique name mapping"""
    with open(MITRE_MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Training parameters
TRAIN_SPLIT = 0.8   # 80% for training
VAL_SPLIT = 0.1     # 10% for validation
TEST_SPLIT = 0.1    # 10% for testing

# Instruction template
INSTRUCTION_TEMPLATE = "Analyze this session log chunk and determine if it contains normal or suspicious activity. If suspicious, identify all MITRE ATT&CK techniques and explain why."

# Validation
def validate_paths():
    """Validate that required input files exist"""
    errors = []
    
    if not SUSPICIOUS_CHUNKS_FILE.exists():
        errors.append(f"Suspicious chunks file not found: {SUSPICIOUS_CHUNKS_FILE}")
    
    if not NORMAL_CHUNKS_FILE.exists():
        errors.append(f"Normal chunks file not found: {NORMAL_CHUNKS_FILE}")
    
    if not MITRE_MAPPING_FILE.exists():
        errors.append(f"MITRE mapping file not found: {MITRE_MAPPING_FILE}")
    
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True


if __name__ == '__main__':
    print("Training Preparation Configuration")
    print("=" * 70)
    print(f"Suspicious chunks: {SUSPICIOUS_CHUNKS_FILE}")
    print(f"Normal chunks: {NORMAL_CHUNKS_FILE}")
    print(f"Output directory: {FINAL_OUTPUT_DIR}")
    print(f"Output format: JSONL (one example per line)")
    print(f"Split: {TRAIN_SPLIT*100:.0f}% train, {VAL_SPLIT*100:.0f}% val, {TEST_SPLIT*100:.0f}% test")
    print("Note: Suspicious and normal chunks are split separately to maintain proper distribution")
    print("=" * 70)
    
    if validate_paths():
        print("✅ All paths are valid!")
    else:
        print("❌ Configuration validation failed!")
