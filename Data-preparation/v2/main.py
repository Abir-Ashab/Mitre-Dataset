"""
Master pipeline script to run the entire data preparation workflow
Runs both suspicious and normal data pipelines sequentially
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import validate_paths
import extract_suspicious_logs
import extract_normal_logs
import clean_suspicious_logs
import clean_normal_logs
import chunk_suspicious_logs
import chunk_normal_logs


def print_pipeline_header(step_num: int, step_name: str):
    """Print a formatted pipeline step header"""
    print("\n\n")
    print("█" * 70)
    print(f"█  STEP {step_num}: {step_name}")
    print("█" * 70)


def run_suspicious_pipeline():
    """Run the suspicious logs pipeline"""
    print("\n" + "="*70)
    print("🔴 SUSPICIOUS LOGS PIPELINE")
    print("="*70)
    
    # Step 1: Extract
    print_pipeline_header(1, "EXTRACT SUSPICIOUS LOGS")
    extract_suspicious_logs.main()
    
    # Step 2: Clean
    print_pipeline_header(2, "CLEAN SUSPICIOUS LOGS")
    clean_suspicious_logs.main()
    
    # Step 3: Chunk
    print_pipeline_header(3, "CREATE SUSPICIOUS CHUNKS")
    chunk_suspicious_logs.main()
    
    print("\n" + "="*70)
    print("✅ SUSPICIOUS PIPELINE COMPLETE")
    print("="*70)


def run_normal_pipeline():
    """Run the normal logs pipeline"""
    print("\n" + "="*70)
    print("🟢 NORMAL LOGS PIPELINE")
    print("="*70)
    
    # Step 1: Extract
    print_pipeline_header(1, "EXTRACT NORMAL LOGS")
    extract_normal_logs.main()
    
    # Step 2: Clean
    print_pipeline_header(2, "CLEAN NORMAL LOGS")
    clean_normal_logs.main()
    
    # Step 3: Chunk
    print_pipeline_header(3, "CREATE NORMAL CHUNKS")
    chunk_normal_logs.main()
    
    print("\n" + "="*70)
    print("✅ NORMAL PIPELINE COMPLETE")
    print("="*70)


def main():
    """Run the complete data preparation pipeline"""
    print("="*70)
    print("🚀 STARTING FULL DATA PREPARATION PIPELINE")
    print("="*70)
    
    # Validate configuration
    print("\n📋 Validating configuration...")
    if not validate_paths():
        print("\n❌ Configuration validation failed. Please check paths.")
        return
    
    print("✅ Configuration valid!\n")
    
    try:
        # Run suspicious pipeline
        run_suspicious_pipeline()
        
        # Run normal pipeline
        run_normal_pipeline()
        
        # Final summary
        print("\n\n")
        print("🎉" * 35)
        print("🎉  PIPELINE COMPLETE - ALL STEPS SUCCESSFUL  🎉")
        print("🎉" * 35)
        print("\nNext steps:")
        print("  1. Review the chunks in training_data/")
        print("  2. Run merge and balancing scripts (coming soon)")
        print("  3. Convert to fine-tuning format")
        print("  4. Split into train/val/test sets")
        
    except Exception as e:
        print("\n\n❌ PIPELINE FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
