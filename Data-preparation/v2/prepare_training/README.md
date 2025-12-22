# Training Data Preparation

Final step in the data preparation pipeline: merge, balance, and split chunks into train/val/test sets ready for fine-tuning.

## 📁 Directory Structure

```
prepare_training/
├── config.py                      # Configuration
├── merge_and_balance.py           # Merge and balance suspicious/normal chunks
├── split_train_val_test.py        # Split into train/val/test by session
├── run_pipeline.py                # Master pipeline runner
├── merged_balanced_chunks.json    # Intermediate: balanced chunks
└── final_training_data/           # Output directory
    ├── train.json                 # Training set (70%)
    ├── val.json                   # Validation set (15%)
    └── test.json                  # Test set (15%)
```

## 🔄 Pipeline Flow

### Step 1: Merge and Balance

**Script:** `merge_and_balance.py`

- Loads suspicious and normal chunks
- Balances them according to `BALANCE_RATIO` (default: 50/50)
- Shuffles chunks
- Output: `merged_balanced_chunks.json`

### Step 2: Split by Session

**Script:** `split_train_val_test.py`

- Groups chunks by session_id
- Splits SESSIONS (not individual chunks) into 70/15/15
- Converts chunks to instruction-tuning format
- Removes labels/techniques from input
- Adds MITRE technique names to output
- Output: `train.json`, `val.json`, `test.json`

## 🚀 Usage

### Run Full Pipeline

```bash
cd E:\Hacking\Mitre-Dataset\Fine-tune-Data-preparation\v2\prepare_training
python run_pipeline.py
```

### Run Individual Steps

```bash
python merge_and_balance.py
python split_train_val_test.py
```

## ⚙️ Configuration

Edit `config.py` to adjust:

- **BALANCE_RATIO**: Ratio of suspicious to total (default: 0.5 = 50% suspicious, 50% normal)
- **TRAIN_SPLIT**: Training set ratio (default: 0.7 = 70%)
- **VAL_SPLIT**: Validation set ratio (default: 0.15 = 15%)
- **TEST_SPLIT**: Test set ratio (default: 0.15 = 15%)

## 📊 Output Format

### Training Example Structure

```json
{
  "instruction": "Analyze this session log chunk and determine if it contains normal or suspicious activity. If suspicious, identify all MITRE ATT&CK techniques and explain why.",
  "input": "{\"metadata\": {...}, \"logs\": [...]}",
  "output": "Status: Suspicious\nMITRE Techniques: T1059.001 (Command and Scripting Interpreter: PowerShell), T1105 (Ingress Tool Transfer)\nReason: Malicious activity detected in 15 out of 20 events based on behavioral patterns and attack signatures"
}
```

### Input Structure (JSON string)

```json
{
  "metadata": {
    "session_id": "20250918_091900",
    "chunk_index": 0,
    "start_time": "2025-09-18T09:19:00Z",
    "end_time": "2025-09-18T09:21:00Z",
    "number_of_events": 20
  },
  "logs": [
    {
      "@timestamp": "2025-09-18T09:19:00Z",
      "event": {...},
      // All original fields except: label, mitre_techniques, session_id
    }
  ]
}
```

### Output for Suspicious

```
Status: Suspicious
MITRE Techniques: T1059.001 (Command and Scripting Interpreter: PowerShell), T1105 (Ingress Tool Transfer)
Reason: Malicious activity detected in 15 out of 20 events based on behavioral patterns and attack signatures
```

### Output for Normal

```
Status: Normal
Reason: Standard system activity with no suspicious indicators across all events
```

## 🎯 Key Features

✅ **Session-based splitting**: All chunks from same session stay in same split  
✅ **Balanced dataset**: Configurable suspicious/normal ratio  
✅ **Clean inputs**: Labels and techniques removed from input  
✅ **Rich outputs**: MITRE techniques with human-readable names  
✅ **Reproducible**: Fixed random seeds  
✅ **Standard splits**: 70/15/15 train/val/test

## 📝 Use Cases

### Fine-tuning

Use the generated files for:

- **Instruction tuning**: Model learns to analyze logs and identify attacks
- **MITRE detection**: Model learns to map behaviors to ATT&CK techniques
- **Binary classification**: Normal vs suspicious
- **Multi-label classification**: Multiple MITRE techniques per example

### Compatible With

- LoRA fine-tuning
- Full fine-tuning
- Parameter-efficient fine-tuning (PEFT)
- Any instruction-tuning framework (Alpaca, etc.)

## 📈 Expected Output Sizes

For balanced 50/50 suspicious/normal:

- If you have 1000 suspicious + 2000 normal chunks
- Balanced: 1000 suspicious + 1000 normal = 2000 total
- Train: ~1400 examples (70%)
- Val: ~300 examples (15%)
- Test: ~300 examples (15%)

## 🔍 Validation

The pipeline ensures:

- No data leakage between splits (session-based splitting)
- Balanced representation in each split
- All original log data preserved in input
- MITRE techniques properly formatted in output
