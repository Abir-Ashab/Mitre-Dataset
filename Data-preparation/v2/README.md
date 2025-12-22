# Fine-Tuning Data Preparation Pipeline v2

Modular pipeline for preparing MITRE ATT&CK detection training data from suspicious and normal logs.

## 📁 Directory Structure

```
v2/
├── config.py                      # Central configuration
├── utils.py                       # Shared utility functions
├── extract_suspicious_logs.py     # Extract suspicious logs
├── extract_normal_logs.py         # Extract normal logs
├── clean_suspicious_logs.py       # Deduplicate suspicious logs
├── clean_normal_logs.py           # Deduplicate normal logs
├── chunk_suspicious_logs.py       # Create suspicious chunks (20 logs each)
├── chunk_normal_logs.py           # Create normal chunks (20 logs each)
├── run_pipeline.py                # Master pipeline runner
├── output/                        # Intermediate files
│   ├── extracted_suspicious_logs.json
│   ├── extracted_normal_logs.json
│   ├── cleaned_suspicious_logs.json
│   └── cleaned_normal_logs.json
└── training_data/                 # Final chunk outputs
    ├── suspicious_chunks.json
    └── normal_chunks.json
```

## 🔄 Pipeline Flow

### Suspicious Logs Pipeline

1. **Extract** (`extract_suspicious_logs.py`)

   - Source: `E:\Hacking\Mitre-Dataset\Annotate-attack-logs\suspicious-logs`
   - Extracts only logs with `label="suspicious"`
   - Skips sessions with no suspicious logs
   - Output: `output/extracted_suspicious_logs.json`

2. **Clean** (`clean_suspicious_logs.py`)

   - Removes exact duplicate logs
   - Preserves all original fields
   - Output: `output/cleaned_suspicious_logs.json`

3. **Chunk** (`chunk_suspicious_logs.py`)
   - Groups by session_id
   - Creates chunks of 20 logs each
   - Sorts logs by timestamp within chunks
   - Output: `training_data/suspicious_chunks.json`

### Normal Logs Pipeline

1. **Extract** (`extract_normal_logs.py`)

   - Source: `E:\Hacking\Mitre-Dataset\Annotate-attack-logs\normal-logs`
   - Extracts all logs (assumes all are normal)
   - Output: `output/extracted_normal_logs.json`

2. **Clean** (`clean_normal_logs.py`)

   - Removes exact duplicate logs
   - Optional: Sample down if too many logs
   - Output: `output/cleaned_normal_logs.json`

3. **Chunk** (`chunk_normal_logs.py`)
   - Groups by session_id
   - Creates chunks of 20 logs each
   - Sorts logs by timestamp within chunks
   - Output: `training_data/normal_chunks.json`

## 🚀 Usage

### Run Full Pipeline

```bash
python run_pipeline.py
```

### Run Individual Steps

**Suspicious logs:**

```bash
python extract_suspicious_logs.py
python clean_suspicious_logs.py
python chunk_suspicious_logs.py
```

**Normal logs:**

```bash
python extract_normal_logs.py
python clean_normal_logs.py
python chunk_normal_logs.py
```

### Validate Configuration

```bash
python config.py
```

## ⚙️ Configuration

Edit `config.py` to adjust:

- `CHUNK_SIZE`: Number of logs per chunk (default: 20)
- `MIN_CHUNK_SIZE`: Minimum logs to form a chunk (default: 10)
- Source/output paths

## 📊 Output Format

### Chunk Structure

```json
{
  "metadata": {
    "session_id": "20250918_091900",
    "chunk_index": 0,
    "chunk_size": 20,
    "start_time": "2025-09-18T09:19:00Z",
    "end_time": "2025-09-18T09:21:00Z"
  },
  "logs": [
    {
      "session_id": "20250918_091900",
      "label": "suspicious",
      "mitre_techniques": ["T1059.001"],
      "@timestamp": "2025-09-18T09:19:00Z"
      // ... all other original fields
    }
    // ... 19 more logs
  ]
}
```

## 🎯 Design Principles

1. **Modular**: Each step is independent and can be run separately
2. **Pure Chunks**: Suspicious and normal chunks are kept separate
3. **Session Integrity**: Logs from same session stay together
4. **Zero Data Loss**: All original fields preserved
5. **Reproducible**: Fixed random seeds for sampling

## 📝 Next Steps

1. **Merge & Balance**: Combine suspicious and normal chunks with proper ratio
2. **Convert to Training Format**: Create instruction-tuning format with MITRE techniques
3. **Train/Val/Test Split**: Split by session (70/15/15)
4. **Fine-tuning**: Use with LoRA or full fine-tuning

## 🔍 Key Differences from v1

- ✅ Separate suspicious/normal data sources
- ✅ Pure chunks (no mixed suspicious/normal)
- ✅ Smaller chunk size (20 vs 30)
- ✅ Skip sessions without suspicious logs
- ✅ More modular architecture
- ✅ Better configurability
