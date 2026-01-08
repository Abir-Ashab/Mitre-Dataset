"""
Configuration file for data preparation pipeline
Centralized configuration for both suspicious and normal data pipelines
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent.parent
ANNOTATE_LOGS_DIR = ROOT_DIR / 'Annotate-attack-logs'

# Source paths
SUSPICIOUS_LOGS_DIR = ANNOTATE_LOGS_DIR / 'suspicious-logs'
NORMAL_LOGS_DIR = ANNOTATE_LOGS_DIR / 'normal-logs'

# Output paths
OUTPUT_DIR = BASE_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Intermediate output files
EXTRACTED_SUSPICIOUS_FILE = OUTPUT_DIR / 'extracted_suspicious_logs.json'
EXTRACTED_NORMAL_FILE = OUTPUT_DIR / 'extracted_normal_logs.json'

CLEANED_SUSPICIOUS_FILE = OUTPUT_DIR / 'cleaned_suspicious_logs.json'
CLEANED_NORMAL_FILE = OUTPUT_DIR / 'cleaned_normal_logs.json'

# Training data paths
TRAINING_DIR = BASE_DIR / 'training_data'
TRAINING_DIR.mkdir(exist_ok=True)

SUSPICIOUS_CHUNKS_FILE = TRAINING_DIR / 'suspicious_chunks.json'
NORMAL_CHUNKS_FILE = TRAINING_DIR / 'normal_chunks.json'

# Processing parameters
CHUNK_SIZE = 7   # Number of logs per chunk (optimized for token efficiency & better learning)
                 # 7 logs ≈ 2,200 tokens (vs 20 logs ≈ 6,315 tokens)
                 # Creates 3x more training examples while staying within token limits
MIN_CHUNK_SIZE = 5  # Minimum logs to form a chunk (for last chunk in session)

# MITRE techniques mapping
MITRE_MAPPING_FILE = BASE_DIR / 'mitre_techniques.json'

# Validation
def validate_paths():
    """Validate that required paths exist"""
    errors = []
    
    if not SUSPICIOUS_LOGS_DIR.exists():
        errors.append(f"Suspicious logs directory not found: {SUSPICIOUS_LOGS_DIR}")
    
    if not NORMAL_LOGS_DIR.exists():
        errors.append(f"Normal logs directory not found: {NORMAL_LOGS_DIR}")
    
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True


if __name__ == '__main__':
    print("Configuration Validation")
    print("=" * 70)
    print(f"Suspicious logs: {SUSPICIOUS_LOGS_DIR}")
    print(f"Normal logs: {NORMAL_LOGS_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Training directory: {TRAINING_DIR}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print("=" * 70)
    
    if validate_paths():
        print("✅ All paths are valid!")
    else:
        print("❌ Configuration validation failed!")
