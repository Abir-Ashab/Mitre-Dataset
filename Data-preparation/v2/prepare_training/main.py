"""
Master script to run the complete training preparation pipeline
1. Merge and balance chunks
2. Convert to instruction-tuning format (NEW: modular SOLID architecture)
3. Split into train/val/test
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import validate_paths, FINAL_OUTPUT_DIR
import merge_and_balance
import convert_to_training_format
import split_train_val_test


def print_step_header(step_num: int, step_name: str):
    """Print a formatted step header"""
    print("\n\n")
    print("=" * 70)
    print(f"  STEP {step_num}: {step_name}")
    print("=" * 70)


def main():
    """Run the complete training preparation pipeline"""
    print("="*70)
    print(" TRAINING DATA PREPARATION PIPELINE (REFACTORED v2.0)")
    print("="*70)
    print(" New Approach:")
    print("   > Field-specific analysis (references actual log fields)")
    print("   > Real attack patterns from documented pen tests")
    print("   > Modular SOLID architecture")
    print("   > Model learns HOW to analyze, not just output format")
    print("="*70)
    print("\nPipeline Steps:")
    print("   [1] Merge & Balance chunks")
    print("   [2] Split into train/val/test with modular conversion (80/10/10)")
    print("="*70)
    
    # Validate configuration
    print("\n[*] Validating configuration...")
    if not validate_paths():
        print("\n[!] Configuration validation failed. Please check paths.")
        return
    
    print("[+] Configuration valid!\n")
    
    try:
        # Step 1: Merge all chunks
        print_step_header(1, "MERGE ALL CHUNKS")
        merge_and_balance.main()
        
        # Step 2: Split into train/val/test (with modular conversion inside)
        print_step_header(2, "SPLIT & CONVERT WITH MODULAR ANALYSIS")
        print("[*] Using NEW modular analyzers with real attack patterns")
        print("   - ProcessAnalyzer: EventID 1, 4688")
        print("   - NetworkAnalyzer: EventID 3, 5156 (C2 detection)")
        print("   - FileAnalyzer: EventID 11, 23 (ransomware detection)")
        print("")
        split_train_val_test.main()
        
        # Final summary
        print("\n\n")
        print("="*70)
        print("  PIPELINE COMPLETE - READY FOR FINE-TUNING  ")
        print("="*70)
        print(f"\n[*] Training data saved to: {FINAL_OUTPUT_DIR}")
        print("\nFiles created (JSONL format):")
        print("  - train.jsonl (training set)")
        print("  - val.jsonl (validation set)")
        print("  - test.jsonl (test set)")
        print("\n[+] Key Improvements:")
        print("   > Outputs reference specific log fields")
        print("   > Explains WHY suspicious/normal based on field values")
        print("   > Uses real attack patterns (C2 IPs, ransomware, creds)")
        print("   > No generic templates - unique analysis per log")
        print("\n[*] Next steps:")
        print("  1. Review sample outputs in terminal above")
        print("  2. Upload train.jsonl to Kaggle dataset")
        print("  3. Retrain model with improved training data")
        print("  4. Evaluate on test.jsonl")
        print("\n[!] Expected: Model will learn log analysis, not format!")
        
    except Exception as e:
        print("\n\n[!] PIPELINE FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
