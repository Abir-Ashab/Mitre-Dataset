"""
Master script to run the complete training preparation pipeline
1. Merge and balance chunks
2. Split into train/val/test
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import validate_paths, FINAL_OUTPUT_DIR
import merge_and_balance
import split_train_val_test


def print_step_header(step_num: int, step_name: str):
    """Print a formatted step header"""
    print("\n\n")
    print("█" * 70)
    print(f"█  STEP {step_num}: {step_name}")
    print("█" * 70)


def main():
    """Run the complete training preparation pipeline"""
    print("="*70)
    print("🚀 TRAINING DATA PREPARATION PIPELINE")
    print("Split: 80% train, 10% val, 10% test")
    print("(Applied separately to suspicious and normal chunks)")
    print("="*70)
    
    # Validate configuration
    print("\n📋 Validating configuration...")
    if not validate_paths():
        print("\n❌ Configuration validation failed. Please check paths.")
        return
    
    print("✅ Configuration valid!\n")
    
    try:
        # Step 1: Merge all chunks
        print_step_header(1, "MERGE ALL CHUNKS")
        merge_and_balance.main()
        
        # Step 2: Split into train/val/test
        print_step_header(2, "SPLIT INTO TRAIN/VAL/TEST")
        split_train_val_test.main()
        
        # Final summary
        print("\n\n")
        print("🎉" * 35)
        print("🎉  PIPELINE COMPLETE - READY FOR FINE-TUNING  🎉")
        print("🎉" * 35)
        print(f"\n📁 Training data saved to: {FINAL_OUTPUT_DIR}")
        print("\nFiles created (JSONL format):")
        print("  - train.jsonl (training set)")
        print("  - val.jsonl (validation set)")
        print("  - test.jsonl (test set)")
        print("\n✅ All data included (no balancing/sampling)")
        print("✅ JSONL format (one JSON object per line)")
        print("\n📚 Next steps:")
        print("  1. Review the generated files")
        print("  2. Use train.jsonl for fine-tuning your model")
        print("  3. Use val.jsonl for validation during training")
        print("  4. Use test.jsonl for final evaluation")
        
    except Exception as e:
        print("\n\n❌ PIPELINE FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
