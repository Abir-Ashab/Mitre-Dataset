# Fine-Tuning Script Documentation
## Complete Parameter and Configuration Explanation

---

## 📋 Table of Contents
1. [Cell 1: GPU Check](#cell-1-gpu-check)
2. [Cell 2: Data Verification](#cell-2-data-verification)
3. [Cell 3: Dependencies Installation](#cell-3-dependencies-installation)
4. [Cell 4: Configuration](#cell-4-configuration)
5. [Cell 5: Model Loading](#cell-5-model-loading)
6. [Cell 6: LoRA Configuration](#cell-6-lora-configuration)
7. [Cell 7: Dataset Loading](#cell-7-dataset-loading)
8. [Cell 8: Token Length Analysis](#cell-8-token-length-analysis)
9. [Cell 9: Dataset Tokenization](#cell-9-dataset-tokenization)
10. [Cell 10: Training Arguments](#cell-10-training-arguments)
11. [Cell 11: Trainer Setup](#cell-11-trainer-setup)
12. [Cell 12: Training Execution](#cell-12-training-execution)
13. [Cell 13: Model Saving](#cell-13-model-saving)
14. [Cell 14: Model Export](#cell-14-model-export)

---

## Cell 1: GPU Check

```python
!nvidia-smi
```

### Purpose
Displays GPU information to verify hardware availability and specifications.

### What It Shows
- **GPU Model**: Type of GPU (e.g., Tesla T4, V100)
- **Memory**: Total VRAM available (e.g., 15GB for T4)
- **Current Usage**: Memory already allocated
- **Driver Version**: CUDA and driver versions

### Why It Matters
- Ensures GPU is available (required for training)
- Helps determine appropriate batch sizes based on VRAM
- Confirms CUDA compatibility

---

## Cell 2: Data Verification

```python
data_path = "/kaggle/input/mitre-dataset"
```

### Purpose
Verifies that training data is properly uploaded and accessible.

### Key Operations
1. **Path Check**: Confirms dataset folder exists
2. **File Listing**: Shows all files and their sizes
3. **JSONL Validation**: Counts examples in train/val/test files

### Expected Output
```
✅ train.jsonl: 89,693 examples
✅ val.jsonl: 12,427 examples
✅ test.jsonl: X examples
```

### Why It Matters
- Prevents training crashes due to missing data
- Confirms data format is correct (JSONL)
- Shows dataset size for planning

---

## Cell 3: Dependencies Installation

```python
!pip install -q transformers datasets accelerate peft
```

### Libraries Installed

| Library | Version | Purpose |
|---------|---------|---------|
| `transformers` | Latest | Hugging Face library for loading/training models |
| `datasets` | Latest | Loading and processing JSONL datasets |
| `accelerate` | Latest | Multi-GPU training and memory optimization |
| `peft` | Latest | Parameter-Efficient Fine-Tuning (LoRA support) |

### Why `-q` Flag?
- Suppresses verbose installation logs
- Keeps output clean and readable

---

## Cell 4: Configuration

### Model Selection
```python
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
```

**Why Qwen2.5-1.5B-Instruct?**
- **Size**: 1.5B parameters - fits in T4 GPU (15GB VRAM)
- **Instruction-Tuned**: Pre-trained for instruction following
- **Performance**: Good balance between speed and accuracy
- **Context Window**: Supports long sequences (up to 32K tokens)

### Path Configuration
```python
DATA_PATH = "/kaggle/input/mitre-dataset"
OUTPUT_DIR = "/kaggle/working/checkpoints"
FINAL_MODEL_DIR = "/kaggle/working/fine_tuned_model"
```

**Why These Paths?**
- `/kaggle/input/*`: Read-only dataset folder (Kaggle standard)
- `/kaggle/working/*`: Writable temporary storage for outputs
- Checkpoints saved during training for recovery
- Final model saved separately for download

### Training Hyperparameters

#### MAX_LENGTH = 4096
**What It Does**: Maximum number of tokens per training example

**Why 4096?**
- Your 7-log chunks average ~2,300 tokens
- 99th percentile is ~6,338 tokens
- 4096 provides headroom without excessive padding
- Longer sequences = more context but slower training

**Trade-offs**:
- ✅ Covers 95%+ of sequences without truncation
- ❌ Longer than necessary = slower training
- 💡 **Recommendation**: Consider reducing to 3072 for faster training

---

#### BATCH_SIZE = 1
**What It Does**: Number of examples processed simultaneously per GPU

**Why 1?**
- **Memory Constraint**: T4 GPU has 15GB VRAM
- Larger batches = more memory usage
- Prevents Out-Of-Memory (OOM) errors
- With gradient accumulation, effective batch is still 16

**Trade-offs**:
- ✅ Prevents OOM crashes
- ❌ Slower training (4x more steps than batch_size=4)
- 💡 **Can increase to 2** if memory allows

---

#### GRAD_ACCUM_STEPS = 16
**What It Does**: Number of forward passes before updating model weights

**How It Works**:
```
Effective Batch Size = BATCH_SIZE × GRAD_ACCUM_STEPS
                     = 1 × 16 = 16 examples per weight update
```

**Why 16?**
- Simulates training with batch_size=16
- Accumulates gradients without memory overhead
- Larger effective batches = more stable training
- Standard for instruction tuning

**Trade-offs**:
- ✅ Better gradient estimates (less noisy)
- ✅ No extra memory cost
- ❌ Slower training (more forward passes)

---

#### NUM_EPOCHS = 5
**What It Does**: Number of complete passes through training data

**Why 5?**
- Typical range for fine-tuning: 3-10 epochs
- More epochs = better learning (up to a point)
- Risk of overfitting after too many epochs
- 5 balances learning vs. overfitting

**Total Training Steps**:
```
Steps per epoch = 89,693 / (1 × 16) = 5,606
Total steps = 5,606 × 5 = 28,030 steps
```

**Trade-offs**:
- ✅ More learning time
- ❌ Longer training (~5-6 hours vs. 2-3 hours for 3 epochs)
- 💡 **Recommendation**: Start with 3 epochs, increase if needed

---

#### LEARNING_RATE = 2e-4
**What It Does**: Controls how much model weights change per update

**Why 2e-4 (0.0002)?**
- Standard for instruction fine-tuning
- Too high = unstable training, divergence
- Too low = slow learning, may not converge
- Proven effective for 1-7B parameter models

**Common Values**:
| Model Size | Learning Rate | Notes |
|------------|---------------|-------|
| < 1B | 3e-4 to 5e-4 | Smaller models need higher LR |
| 1-7B | **2e-4** | Sweet spot for most models |
| 7B+ | 1e-4 to 5e-5 | Large models sensitive to LR |

**With Cosine Scheduler**:
- Starts at 2e-4 (after warmup)
- Gradually decreases to ~0 by end of training
- Helps model converge smoothly

---

## Cell 5: Model Loading

### Model Loading Parameters

```python
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
```

#### torch_dtype=torch.float16
**What It Does**: Loads model in half-precision (FP16) format

**Why FP16?**
- **Memory Savings**: Uses 50% less VRAM than FP32
  - FP32: 1.5B × 4 bytes = 6GB
  - FP16: 1.5B × 2 bytes = **3GB** ✅
- **Speed**: 2-3x faster computation on modern GPUs
- **Accuracy**: Minimal loss for fine-tuning tasks

**Alternatives**:
| Format | Memory | Speed | Accuracy | When to Use |
|--------|--------|-------|----------|-------------|
| FP32 | 6GB | 1x | 100% | Maximum precision needed |
| **FP16** | **3GB** | **2-3x** | **99.9%** | **Default choice** ✅ |
| INT8 | 1.5GB | 1.5x | 98% | Extreme memory constraint |
| INT4 | 0.75GB | 1x | 95% | Inference only |

---

#### device_map="auto"
**What It Does**: Automatically distributes model across available GPUs/CPU

**How It Works**:
- Analyzes available hardware (GPU memory, CPU RAM)
- Splits model layers optimally
- Moves layers to GPU until memory full, rest to CPU

**For Single T4 GPU**:
- All layers fit in GPU → Full GPU acceleration ✅
- If OOM → Automatically offloads some layers to CPU

**For Multi-GPU**:
- Distributes layers across GPUs evenly
- Enables training larger models

---

#### trust_remote_code=True
**What It Does**: Allows execution of custom model code from Hugging Face Hub

**Why Needed for Qwen?**
- Qwen models use custom architecture code
- Not in standard transformers library
- Downloads from model repository

**Security Note**:
- ⚠️ Only use with trusted models (Qwen is official)
- Custom code could theoretically be malicious

---

### Tokenizer Configuration

```python
tokenizer.pad_token = tokenizer.eos_token
```

**Why Set pad_token?**
- Some models (like Qwen) don't have a dedicated pad token
- Uses End-Of-Sequence (EOS) token for padding
- Required for batch processing with variable-length sequences

**How Padding Works**:
```
Example 1: [1, 2, 3, 4, 5]           → Length 5
Example 2: [6, 7, 8]                 → Length 3
Batched:   [1, 2, 3, 4, 5]
           [6, 7, 8, <pad>, <pad>]   → Padded to length 5
```

---

## Cell 6: LoRA Configuration

### What is LoRA?
**LoRA (Low-Rank Adaptation)** is a parameter-efficient fine-tuning method.

**Instead of updating all 1.5B parameters**:
- Freezes original model weights (1.5B params)
- Adds small trainable "adapter" matrices (~30M params)
- Only trains the adapters (2% of model size)

**Benefits**:
| Aspect | Full Fine-Tuning | LoRA |
|--------|------------------|------|
| Trainable Params | 1.5B (100%) | 30M (2%) |
| Memory Usage | High | **Low** ✅ |
| Training Speed | Slow | **Fast** ✅ |
| Storage | 6GB per model | **120MB per model** ✅ |
| Quality | Slightly better | Nearly identical |

---

### Gradient Checkpointing

```python
model.gradient_checkpointing_enable()
model.config.use_cache = False
```

#### gradient_checkpointing_enable()
**What It Does**: Trades computation for memory

**How It Works**:
- **Normal**: Stores all intermediate activations in memory
  - Forward pass: Store activations (uses VRAM)
  - Backward pass: Use stored activations (fast)
  
- **With Checkpointing**: Only stores subset of activations
  - Forward pass: Store some activations (less VRAM)
  - Backward pass: Recompute missing activations (slower but saves memory)

**Trade-offs**:
- ✅ Reduces memory by 30-40%
- ❌ Training ~20% slower (recomputation overhead)
- 💡 Essential for large models on limited VRAM

---

#### use_cache = False
**Why Disable Cache?**
- **With Cache**: Model stores attention scores for faster inference
- **Incompatible** with gradient checkpointing
- Not needed during training (only useful for generation)
- Must be disabled to avoid errors

---

### Model Weight Preparation

```python
for param in model.parameters():
    param.requires_grad = False
    if param.ndim == 1:
        param.data = param.data.to(torch.float32)
```

#### param.requires_grad = False
**What It Does**: Freezes all base model parameters

**Why?**
- LoRA only trains adapter weights
- Prevents accidental updates to base model
- Reduces memory and computation

---

#### Cast LayerNorms to FP32
```python
if param.ndim == 1:
    param.data = param.data.to(torch.float32)
```

**What It Does**: Keeps normalization layers in full precision

**Why?**
- **1D parameters** = LayerNorm weights (mean/variance calculations)
- **Normalization** is sensitive to precision errors
- FP16 can cause training instability in normalization
- Mixed precision best practice: FP16 matmul, FP32 normalization

**Impact**:
- Adds ~10MB memory usage
- Significantly improves training stability
- Standard practice in modern fine-tuning

---

### LoRA Hyperparameters

```python
lora_config = LoraConfig(
    r=32,
    lora_alpha=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

#### r=32 (Rank)
**What It Does**: Controls size of adapter matrices

**How It Works**:
```
Original weight: W (4096 × 4096)
LoRA decomposition: W + A × B
  where A (4096 × r), B (r × 4096)

r=32: 4096×32 + 32×4096 = 262,144 params per layer
r=64: 4096×64 + 64×4096 = 524,288 params per layer
```

**Why 32?**
- Higher rank = more capacity, better learning
- Lower rank = fewer params, faster training
- 32 is optimal for 1-7B models
- Provides good balance

**Common Values**:
| Rank | Model Size | Quality | Speed |
|------|------------|---------|-------|
| 8 | < 1B | Good | Fast |
| 16 | 1-3B | Very Good | Fast |
| **32** | **1-7B** | **Excellent** ✅ | **Balanced** |
| 64 | 7B+ | Best | Slower |

---

#### lora_alpha=64
**What It Does**: Scaling factor for adapter updates

**Formula**:
```
Adapter contribution = (lora_alpha / r) × adapter_weights
                     = (64 / 32) × adapter_weights
                     = 2 × adapter_weights
```

**Why alpha = 2 × r?**
- **Standard practice**: alpha = 2 × r
- Balances adapter strength
- Too high = unstable training
- Too low = slow learning

**Rule of Thumb**:
- r=8 → alpha=16
- r=16 → alpha=32
- r=32 → **alpha=64** ✅
- r=64 → alpha=128

---

#### target_modules
```python
target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
```

**What It Does**: Specifies which layers get LoRA adapters

**Attention Mechanism Breakdown**:
| Module | Full Name | Function | Why Train It? |
|--------|-----------|----------|---------------|
| **q_proj** | Query Projection | What to look for | Critical for understanding |
| **k_proj** | Key Projection | What to match | Critical for context |
| **v_proj** | Value Projection | What to extract | Critical for information |
| **o_proj** | Output Projection | Combine results | Critical for coherence |

**Why These 4?**
- **Attention is key** in transformers
- These modules learn task-specific patterns
- Updating all 4 provides comprehensive adaptation

**Other Options**:
- **Q+V only**: Faster, slightly lower quality
- **All linear layers**: Better quality, more memory
- **Q+K+V+O**: **Best balance** ✅ (current choice)

---

#### lora_dropout=0.05
**What It Does**: Randomly zeros 5% of adapter neurons during training

**Why Dropout?**
- **Regularization**: Prevents overfitting
- Forces model to learn robust patterns
- Standard practice in deep learning

**Why 5%?**
- 0% = No regularization (risk overfitting)
- 5-10% = **Optimal** for LoRA ✅
- 20%+ = Too aggressive (underfitting)

---

#### bias="none"
**What It Does**: Doesn't train bias terms

**Why?**
- LoRA focuses on weight matrices
- Bias terms have minimal impact
- Saves parameters and computation

**Options**:
| Value | Trains Bias? | When to Use |
|-------|--------------|-------------|
| **"none"** | ❌ | **Default** - most efficient ✅ |
| "lora_only" | Only in LoRA layers | Slight quality boost |
| "all" | All bias terms | Maximum quality, slower |

---

#### task_type="CAUSAL_LM"
**What It Does**: Specifies fine-tuning task type

**Options**:
| Task Type | Description | Use Case |
|-----------|-------------|----------|
| **CAUSAL_LM** | Language modeling | **Text generation, instruction following** ✅ |
| SEQ_2_SEQ_LM | Sequence-to-sequence | Translation, summarization |
| SEQ_CLS | Sequence classification | Sentiment analysis |
| TOKEN_CLS | Token classification | Named entity recognition |

**Why CAUSAL_LM?**
- Your task: MITRE ATT&CK classification (generative task)
- Autoregressive generation (predict next token)
- Standard for instruction tuning

---

## Cell 7: Dataset Loading

```python
dataset = load_dataset(
    'json',
    data_files={
        'train': TRAIN_FILE,
        'validation': VAL_FILE
    }
)
```

### Dataset Format
**Expected JSONL Structure**:
```json
{"instruction": "...", "input": "...", "output": "..."}
{"instruction": "...", "input": "...", "output": "..."}
```

### Why Separate Train/Val?
- **Training Set** (89,693): Model learns from these
- **Validation Set** (12,427): Monitors overfitting
- **No Test Set in Training**: Save for final evaluation

---

## Cell 8: Token Length Analysis

### Purpose
Analyzes actual token lengths to validate MAX_LENGTH setting.

### Why Sample 1000 Examples?
```python
sample_size = min(1000, len(dataset['train']))
```
- Balances accuracy vs. speed
- 1000 examples = representative sample
- Takes ~1 minute vs. ~60 minutes for all 89K

### Statistics Explained

```python
print(f"   Min:     {token_lengths.min():,} tokens")
print(f"   Max:     {token_lengths.max():,} tokens")
print(f"   Mean:    {token_lengths.mean():,.0f} tokens")
print(f"   Median:  {np.median(token_lengths):,.0f} tokens")
print(f"   95th %:  {np.percentile(token_lengths, 95):,.0f} tokens")
print(f"   99th %:  {np.percentile(token_lengths, 99):,.0f} tokens")
```

**Example Output**:
```
Min:     450 tokens     ← Shortest sequence
Max:     10,229 tokens  ← Longest sequence (outlier)
Mean:    2,307 tokens   ← Average length
Median:  1,708 tokens   ← Middle value (50% shorter, 50% longer)
95th %:  5,215 tokens   ← 95% of sequences fit under this
99th %:  6,338 tokens   ← 99% of sequences fit under this
```

**How to Use This**:
| Metric | Recommendation |
|--------|----------------|
| 95th percentile | **Conservative MAX_LENGTH** |
| 99th percentile | **Balanced MAX_LENGTH** ✅ |
| Max | Avoid (usually outliers) |

**For Your Data**:
- 99th %tile = 6,338
- MAX_LENGTH = 4096 → **5% truncation** ⚠️
- **Recommendation**: Increase to **3072** (covers 95%, faster) or **6400** (covers 99%)

---

## Cell 9: Dataset Tokenization

### Prompt Format

```python
def format_prompt(example):
    return f"""{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
```

**Why This Format?**
- **Clear Structure**: Separates instruction, input, output
- **Standard Convention**: Common in instruction tuning
- **Model Understanding**: Qwen trained on similar format

**Example**:
```
Classify the following MITRE ATT&CK technique based on system logs.

### Input:
[Log Entry 1]
[Log Entry 2]
...

### Response:
T1059.001 - PowerShell
```

---

### Tokenization Parameters

```python
tokenized = tokenizer(
    texts,
    truncation=True,
    max_length=MAX_LENGTH,
    padding=False
)
```

#### truncation=True
**What It Does**: Cuts sequences longer than MAX_LENGTH

**Example**:
```
Input: [1, 2, 3, ..., 5000] (5000 tokens)
MAX_LENGTH: 4096
Output: [1, 2, 3, ..., 4096] (truncated)
```

**Trade-off**:
- ✅ Prevents memory issues
- ❌ Loses information from long sequences

---

#### padding=False
**Why No Padding Here?**
- **Dynamic Padding**: DataCollator handles padding per batch
- More efficient than padding all to MAX_LENGTH

**Without Dynamic Padding** (padding=True, pad_to_max_length=True):
```
Example 1: [1, 2, 3, ..., 2000, <pad>, <pad>, ..., <pad>]  ← 2096 pads
Example 2: [4, 5, 6, ..., 1500, <pad>, <pad>, ..., <pad>]  ← 2596 pads
Both padded to 4096 → Waste 50%+ computation!
```

**With Dynamic Padding** (padding=False):
```
Batch 1: [1, 2, 3, ..., 2000]                ← 2000 tokens
         [4, 5, 6, ..., 1500, <pad>, <pad>]  ← Padded to 2000 (longest in batch)
Only 500 pads vs. 4692 pads! 90% reduction ✅
```

---

### Label Masking (Critical!)

```python
tokenized["labels"] = copy.deepcopy(tokenized["input_ids"])
```

**Why deepcopy?**
- Preserves exact same data structure as input_ids
- Prevents reference issues (changing one affects the other)
- Ensures same length (critical for training)

---

```python
for k in range(mask_until):
    labels[k] = -100
```

**What is -100?**
- **Special value** in PyTorch loss functions
- **Ignored in loss calculation**
- Only compute loss on response, not instruction/input

**Why Mask Instruction/Input?**

**Without Masking**:
```
Loss computed on entire sequence:
  Instruction: "Classify..."  ← Wastes compute (no learning)
  Input: "[Log entries...]"    ← Wastes compute (no learning)
  Response: "T1059.001..."     ← Actual learning target ✅
```

**With Masking**:
```
Loss only on Response:
  Instruction: -100, -100, ...  ← Ignored
  Input: -100, -100, ...        ← Ignored  
  Response: "T1059.001..."      ← Full focus ✅
```

**Benefits**:
- Faster training (less computation)
- Better learning (focuses on relevant tokens)
- Standard practice in instruction tuning

---

### Marker Detection

```python
response_markers = [
    "\n\n### Response:\n",
    "### Response:\n", 
    "### Response:"
]
```

**Why Multiple Markers?**
- Tokenization varies (whitespace, special tokens)
- Tries most specific first, falls back to simpler
- Increases detection success rate

**Fallback Strategy**:
```python
if not marker_found:
    split_point = int(len(input_ids) * 0.3)
```

**Why 30%?**
- Assumes instruction + input = ~30% of sequence
- Response = ~70% of sequence
- Conservative estimate if marker not found

---

## Cell 10: Training Arguments

### Batch and Accumulation

```python
per_device_train_batch_size=BATCH_SIZE,          # 1
per_device_eval_batch_size=BATCH_SIZE,           # 1
gradient_accumulation_steps=GRAD_ACCUM_STEPS,    # 16
```

**Effective Batch Size** = 1 × 16 = **16**

**Why Match Train and Eval Batch Size?**
- Consistent memory usage
- Faster evaluation (same as training speed)

---

### Mixed Precision Training

```python
fp16=True,
```

**What It Does**: Uses FP16 for computation, FP32 for critical operations

**Speed Comparison**:
| Precision | Speed | Memory | Accuracy |
|-----------|-------|--------|----------|
| FP32 | 1x | 2x | 100% |
| **FP16** | **2-3x** ✅ | **1x** | 99.9% |

**Automatic Loss Scaling**:
- Prevents gradient underflow (FP16 limitation)
- Dynamically adjusts to maintain numerical stability

---

### Logging and Evaluation

```python
logging_steps=25,
eval_strategy="steps",
eval_steps=100,
```

#### logging_steps=25
**What It Does**: Prints training metrics every 25 steps

**Sample Output**:
```
Step 25: loss=2.341, lr=0.00019
Step 50: loss=2.189, lr=0.00018
```

**Why 25?**
- Frequent enough to monitor progress
- Not too frequent to spam logs
- ~every 1-2 minutes

---

#### eval_steps=100
**What It Does**: Runs validation every 100 steps

**What Gets Evaluated**:
```
Step 100: eval_loss=2.156
Step 200: eval_loss=2.034
Step 300: eval_loss=1.987
```

**Why Evaluate?**
- Detects overfitting early
- Monitors generalization
- Enables early stopping

**Why 100 vs. 25?**
- Evaluation is slow (~5 minutes for 12K examples)
- Too frequent = wasted time
- 100 steps = ~every 10 minutes

---

### Checkpoint Management

```python
save_strategy="steps",
save_steps=200,
save_total_limit=3,
load_best_model_at_end=True,
```

#### save_steps=200
**What It Saves**: Complete model checkpoint every 200 steps

**Checkpoint Contents**:
- Model weights
- Optimizer state
- Training progress
- ~500MB per checkpoint

**Why 200?**
- Recovery points if training crashes
- Less frequent = less disk I/O
- Keeps training smooth

---

#### save_total_limit=3
**What It Does**: Only keeps 3 most recent checkpoints

**Example**:
```
Step 200: checkpoint-200 saved
Step 400: checkpoint-400 saved
Step 600: checkpoint-600 saved
Step 800: checkpoint-800 saved ← checkpoint-200 deleted
```

**Why Limit?**
- Saves disk space (500MB × 3 = 1.5GB vs. 50GB)
- Keeps most recent models
- Older checkpoints usually not needed

---

#### load_best_model_at_end=True
**What It Does**: Loads checkpoint with lowest validation loss after training

**Example**:
```
Step 1000: val_loss=2.1
Step 2000: val_loss=1.9  ← Best
Step 3000: val_loss=2.0

After training: Loads checkpoint from step 2000 ✅
```

**Why?**
- Final checkpoint may be overfit
- Best validation = best generalization
- Automatic model selection

---

### Optimization Parameters

```python
warmup_ratio=0.1,
weight_decay=0.01,
max_grad_norm=1.0,
```

#### warmup_ratio=0.1
**What It Does**: Gradually increases learning rate for first 10% of training

**Learning Rate Schedule**:
```
Steps 0-2800 (10%):  LR: 0 → 2e-4  (warmup)
Steps 2800-28030:    LR: 2e-4 → 0  (cosine decay)
```

**Why Warmup?**
- Prevents large updates early in training
- Stabilizes optimization
- Standard practice

**Visualization**:
```
LR
 |  /‾‾‾‾‾‾‾\___
 | /            \___
 |/                  \___
 +-----------------------> Steps
   Warmup    Training
```

---

#### weight_decay=0.01
**What It Does**: L2 regularization on model weights

**Formula**:
```
Loss = CrossEntropy + 0.01 × ||weights||²
```

**Why?**
- **Prevents overfitting**: Penalizes large weights
- **Improves generalization**: Simpler models
- **Standard value**: 0.01 works for most tasks

**Trade-offs**:
| Value | Effect |
|-------|--------|
| 0.0 | No regularization (may overfit) |
| **0.01** | **Balanced** ✅ |
| 0.1 | Strong regularization (may underfit) |

---

#### max_grad_norm=1.0
**What It Does**: Clips gradients to maximum norm of 1.0

**Why Gradient Clipping?**
- Prevents **exploding gradients**
- Stabilizes training on long sequences
- Standard safety mechanism

**How It Works**:
```python
if gradient_norm > 1.0:
    gradient = gradient × (1.0 / gradient_norm)
```

**Example**:
```
Gradient norm = 5.0 (too large!)
After clipping: 5.0 × (1.0 / 5.0) = 1.0 ✅
```

---

### AdamW Optimizer

```python
optim="adamw_torch",
adam_beta1=0.9,
adam_beta2=0.999,
adam_epsilon=1e-8,
```

#### Why AdamW?
**AdamW** = Adam + **Decoupled Weight Decay**

| Optimizer | When to Use |
|-----------|-------------|
| SGD | Simple tasks, small models |
| Adam | General purpose |
| **AdamW** | **LLM fine-tuning** ✅ (industry standard) |

---

#### adam_beta1=0.9
**What It Does**: Exponential moving average of gradients

**Controls**:
- How much gradient history to use
- Higher = more smoothing
- Lower = more responsive

**Standard Values**:
| beta1 | Use Case |
|-------|----------|
| 0.9 | **Default** ✅ |
| 0.95 | More stable, slower |
| 0.8 | Less stable, faster |

---

#### adam_beta2=0.999
**What It Does**: Exponential moving average of squared gradients

**Controls**:
- Adaptive learning rates per parameter
- Higher = more stable
- Almost always 0.999

---

#### adam_epsilon=1e-8
**What It Does**: Numerical stability constant

**Prevents Division by Zero**:
```python
update = gradient / (sqrt(variance) + epsilon)
```

**Why 1e-8?**
- Small enough to not affect updates
- Large enough to prevent overflow
- Standard value across frameworks

---

### Learning Rate Scheduler

```python
lr_scheduler_type="cosine",
```

**Cosine Schedule**:
```
LR
 |   /‾‾‾\
 |  /      \
 | /        \___
 |/             \___
 +-------------------> Steps
   Warm  Train  Fine-tune
```

**Why Cosine?**
- **Early training**: High LR for fast learning
- **Mid training**: Gradual decrease
- **Late training**: Very low LR for fine-tuning
- **Better than constant**: Improves final convergence

**Alternatives**:
| Scheduler | Behavior | Best For |
|-----------|----------|----------|
| constant | Same LR always | Quick experiments |
| linear | Linear decay | Simple tasks |
| **cosine** | **Smooth decay** ✅ | **LLM fine-tuning** |
| polynomial | Custom decay | Advanced tuning |

---

### Label Smoothing

```python
label_smoothing_factor=0.1,
```

**What It Does**: Softens hard labels to prevent overconfidence

**Without Label Smoothing**:
```
Target probability:
Correct token: 1.0
All other tokens: 0.0
```

**With label_smoothing=0.1**:
```
Correct token: 0.9 (1.0 - 0.1)
All other tokens: 0.1 / vocab_size
```

**Why?**
- **Prevents overconfidence**: Model less certain
- **Better calibration**: More realistic probabilities
- **Improves generalization**: Reduces overfitting

**Standard Values**:
| Value | Effect |
|-------|--------|
| 0.0 | No smoothing (may overfit) |
| **0.1** | **Recommended** ✅ |
| 0.2 | Aggressive smoothing (may underfit) |

---

### Advanced Settings

```python
report_to="none",
gradient_checkpointing=True,
gradient_checkpointing_kwargs={"use_reentrant": False},
logging_first_step=True,
logging_nan_inf_filter=True,
dataloader_num_workers=0,
dataloader_pin_memory=True,
```

#### report_to="none"
**What It Does**: Disables automatic logging to external services

**Options**:
| Value | Logs To |
|-------|---------|
| **"none"** | **Console only** ✅ |
| "tensorboard" | TensorBoard |
| "wandb" | Weights & Biases |
| "mlflow" | MLflow |

**Why "none"?**
- Simplicity (no external setup)
- Kaggle doesn't need external logging
- Can always add later if needed

---

#### gradient_checkpointing=True
(Already explained in Cell 6)

---

#### use_reentrant=False
**What It Does**: Uses newer gradient checkpointing implementation

**Why False?**
- **Older method** (reentrant=True): Can have memory leaks
- **Newer method** (reentrant=False): More stable ✅
- **Recommended** by PyTorch for new code

---

#### logging_first_step=True
**What It Does**: Logs metrics at step 1

**Why?**
- Confirms training started
- Shows initial loss (baseline)
- Useful for debugging

---

#### logging_nan_inf_filter=True
**What It Does**: Filters out NaN/Inf from logs

**Why?**
- Prevents log spam if training diverges
- Makes logs readable
- Standard safety measure

---

#### dataloader_num_workers=0
**What It Does**: Uses main process for data loading (no multiprocessing)

**Why 0?**
- **Avoids multiprocessing issues** on Kaggle
- Simpler debugging
- Minimal speed impact with small batches

**When to Use > 0?**
- Large batch sizes (4+)
- CPU-intensive preprocessing
- Multi-GPU training

---

#### dataloader_pin_memory=True
**What It Does**: Keeps data in pinned (non-pageable) CPU memory

**Why?**
- **Faster GPU transfer**: Direct memory access
- **Small overhead**: ~100MB extra RAM
- **Standard practice** for GPU training

**Speed Improvement**:
- Without pinning: ~0.5 sec per batch
- With pinning: **~0.3 sec per batch** ✅ (40% faster)

---

## Cell 11: Trainer Setup

### Data Collator

```python
data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    label_pad_token_id=-100,
    pad_to_multiple_of=8
)
```

#### Why DataCollatorForSeq2Seq?
**Designed for sequence-to-sequence tasks** (like instruction tuning)

**Features**:
- ✅ Handles different length sequences
- ✅ Pads input_ids and labels separately
- ✅ Dynamic padding per batch
- ✅ Attention mask generation

**Alternatives**:
| Collator | Best For |
|----------|----------|
| DataCollatorForLanguageModeling | Pretraining |
| **DataCollatorForSeq2Seq** | **Instruction tuning** ✅ |
| DataCollator | Custom tasks |

---

#### label_pad_token_id=-100
**Why -100?**
- PyTorch CrossEntropyLoss **ignores** -100
- Ensures padding tokens don't affect loss
- Matches label masking strategy

**Example**:
```
Input:  [1, 2, 3, <pad>, <pad>]
Labels: [4, 5, 6,  -100,  -100]  ← Loss only on 4, 5, 6
```

---

#### pad_to_multiple_of=8
**What It Does**: Pads sequences to multiples of 8

**Why 8?**
- **GPU Tensor Cores** work best with multiples of 8
- **Speed Boost**: 10-15% faster matrix operations
- Minimal waste (max 7 extra tokens per sequence)

**Example**:
```
Sequence 1: 1450 tokens → Padded to 1456 (1450 + 6)
Sequence 2: 2003 tokens → Padded to 2008 (2003 + 5)
```

---

### Early Stopping

```python
early_stopping = EarlyStoppingCallback(
    early_stopping_patience=5,
    early_stopping_threshold=0.005
)
```

#### early_stopping_patience=5
**What It Does**: Stops training if no improvement for 5 consecutive evaluations

**How It Works**:
```
Eval 1: val_loss=2.0  ← Best
Eval 2: val_loss=2.1  (worse, patience: 1)
Eval 3: val_loss=2.0  (tie, patience: 2)
Eval 4: val_loss=2.05 (worse, patience: 3)
Eval 5: val_loss=2.1  (worse, patience: 4)
Eval 6: val_loss=2.15 (worse, patience: 5) → STOP ❌
```

**Why 5?**
- Too low (1-2): Stops too early (underfitting)
- **Balanced (5)**: Good detection ✅
- Too high (10+): Wastes time on overfitting

---

#### early_stopping_threshold=0.005
**What It Does**: Minimum improvement to reset patience

**How It Works**:
```
Current best: 2.000
New val_loss: 1.998 (improvement: 0.002 < 0.005) → Doesn't count ❌
New val_loss: 1.994 (improvement: 0.006 > 0.005) → Counts! ✅
```

**Why 0.005?**
- Ignores noise (small fluctuations)
- Focuses on meaningful improvements
- Prevents premature stopping

---

## Cell 12: Training Execution

```python
train_result = trainer.train()
```

**What Happens During Training**:

1. **Initialization** (10 sec)
   - Load data into memory
   - Initialize optimizer
   - Setup gradient checkpointing

2. **Training Loop** (4-6 hours)
   ```python
   for epoch in range(NUM_EPOCHS):
       for batch in train_dataloader:
           # Forward pass
           outputs = model(batch)
           loss = compute_loss(outputs, labels)
           
           # Backward pass
           loss.backward()
           
           # Update weights (every 16 steps)
           if step % GRAD_ACCUM_STEPS == 0:
               optimizer.step()
               optimizer.zero_grad()
           
           # Evaluate (every 100 steps)
           if step % eval_steps == 0:
               eval_loss = evaluate()
               if early_stopping_triggered:
                   break
   ```

3. **Final Evaluation** (5 min)
   - Compute validation metrics
   - Load best checkpoint
   - Report final results

---

### Training Metrics Explained

```python
print(f"📊 Final training loss: {train_result.training_loss:.4f}")
print(f"📊 Final validation loss: {final_metrics['eval_loss']:.4f}")
print(f"📊 Perplexity: {np.exp(final_metrics['eval_loss']):.2f}")
```

#### Training Loss
**What It Means**: Average loss on training data

**Interpretation**:
| Loss | Model State |
|------|-------------|
| > 3.0 | Barely learning |
| 2.0-3.0 | Learning slowly |
| 1.0-2.0 | **Good learning** ✅ |
| < 1.0 | **Excellent** or overfitting ⚠️ |

---

#### Validation Loss
**What It Means**: Loss on unseen data

**How to Use**:
```
If val_loss << train_loss → Underfitting (model too simple)
If val_loss ≈ train_loss  → Good fit ✅
If val_loss >> train_loss → Overfitting (model memorizing)
```

**Example**:
```
train_loss=1.2, val_loss=1.3 → Good! ✅
train_loss=0.8, val_loss=2.5 → Overfitting ⚠️
```

---

#### Perplexity
**What It Is**: exp(loss) - intuitively "how confused the model is"

**Formula**:
```
Perplexity = e^(loss)

Loss 1.0 → Perplexity 2.7  (model has ~3 good guesses)
Loss 2.0 → Perplexity 7.4  (model has ~7 good guesses)
Loss 3.0 → Perplexity 20.1 (model very confused)
```

**Interpretation**:
| Perplexity | Quality |
|------------|---------|
| < 10 | **Excellent** ✅ |
| 10-20 | Good |
| 20-50 | Acceptable |
| > 50 | Poor |

---

## Cell 13: Model Saving

```python
model.save_pretrained(FINAL_MODEL_DIR)
tokenizer.save_pretrained(FINAL_MODEL_DIR)
```

### What Gets Saved

**Model Files**:
```
fine_tuned_model/
├── adapter_config.json       ← LoRA configuration
├── adapter_model.safetensors ← LoRA weights (~120MB)
├── special_tokens_map.json
├── tokenizer_config.json
├── tokenizer.json
└── vocab.json
```

**Why Separate Files?**
- **Base model**: Not saved (still at Qwen/Qwen2.5-1.5B-Instruct)
- **Adapters only**: 120MB vs. 6GB (50x smaller!) ✅
- **Portable**: Share adapters, others load base + your adapters

---

## Cell 14: Model Export

```python
!zip -r fine_tuned_model.zip {FINAL_MODEL_DIR}
```

### Why Zip?
- **Compression**: 120MB → ~40MB (3x smaller)
- **Single file**: Easier to download/share
- **Standard format**: Works everywhere

---

## 📊 Summary Table: Key Parameters

| Parameter | Value | Why This Value? | Alternative |
|-----------|-------|-----------------|-------------|
| **Model** | Qwen2.5-1.5B | Fits in T4 GPU | Qwen2.5-7B (needs A100) |
| **MAX_LENGTH** | 4096 | Covers 95%+ sequences | 3072 (faster, 95%) |
| **BATCH_SIZE** | 1 | Prevents OOM | 2 (if memory allows) |
| **GRAD_ACCUM** | 16 | Effective batch=16 | 8 (faster, less stable) |
| **NUM_EPOCHS** | 5 | Good learning | 3 (faster, may underfit) |
| **LEARNING_RATE** | 2e-4 | Standard for 1-7B | 3e-4 (for smaller models) |
| **LoRA Rank** | 32 | Balanced capacity | 64 (better, slower) |
| **LoRA Alpha** | 64 | 2 × rank | Must match rank ratio |
| **Warmup** | 10% | Stable start | 5% (faster warmup) |
| **Weight Decay** | 0.01 | Prevents overfitting | 0.1 (stronger reg.) |
| **Label Smoothing** | 0.1 | Better calibration | 0.0 (no smoothing) |

---

## 🎯 Performance Trade-offs

### Training Speed vs. Quality

| Configuration | Speed | Quality | Memory | Recommended For |
|---------------|-------|---------|--------|-----------------|
| Current (batch=1, max_len=4096, epochs=5) | Slow (6h) | High | 12GB | **Best quality** |
| Fast (batch=2, max_len=3072, epochs=3) | **Fast (2h)** | Medium | 10GB | **Quick iteration** ✅ |
| Balanced (batch=2, max_len=3072, epochs=5) | Medium (3h) | **High** | 10GB | **Best overall** ✅ |

---

## 🚨 Common Issues and Solutions

### OOM Error
**Symptoms**: CUDA out of memory

**Solutions**:
1. ✅ Reduce BATCH_SIZE: 1 → **1** (already minimal)
2. ✅ Reduce MAX_LENGTH: 4096 → **3072**
3. ✅ Enable gradient_checkpointing: **True** ✅
4. ⚠️ Use quantization (but reduces quality)

---

### Training Too Slow
**Symptoms**: 278 hours estimated time

**Solutions**:
1. ✅ Reduce MAX_LENGTH: 4096 → **3072** (25% faster)
2. ✅ Reduce NUM_EPOCHS: 5 → **3** (40% faster)
3. ✅ Increase BATCH_SIZE: 1 → **2** (2x faster, if memory allows)
4. ✅ Reduce GRAD_ACCUM: 16 → **8** (2x faster, less stable)

**Combined Impact**:
```
Current: 6 hours
Optimized: 2-3 hours ✅ (3x faster)
```

---

### Overfitting
**Symptoms**: val_loss > train_loss and increasing

**Solutions**:
1. ✅ Increase weight_decay: 0.01 → **0.05**
2. ✅ Increase lora_dropout: 0.05 → **0.1**
3. ✅ Reduce NUM_EPOCHS: 5 → **3**
4. ✅ Early stopping will catch this automatically ✅

---

### Underfitting
**Symptoms**: val_loss ≈ train_loss but both high

**Solutions**:
1. ✅ Increase NUM_EPOCHS: 5 → **7**
2. ✅ Increase LoRA rank: 32 → **64**
3. ✅ Increase LEARNING_RATE: 2e-4 → **3e-4**
4. ✅ Remove label_smoothing: 0.1 → **0.0**

---

## 💡 Optimization Recommendations

### For Faster Training (2-3 hours)
```python
MAX_LENGTH = 3072           # ← Change from 4096
BATCH_SIZE = 2              # ← Change from 1
GRAD_ACCUM_STEPS = 8        # ← Change from 16
NUM_EPOCHS = 3              # ← Change from 5
```

### For Better Quality (6-8 hours)
```python
MAX_LENGTH = 6400           # ← Covers 99%
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
NUM_EPOCHS = 7              # ← More training
lora_config.r = 64          # ← More capacity
```

### For Balanced (4-5 hours) ✅ RECOMMENDED
```python
MAX_LENGTH = 3072           # ← Faster
BATCH_SIZE = 2              # ← Better GPU use
GRAD_ACCUM_STEPS = 8        # ← Faster updates
NUM_EPOCHS = 5              # ← Good learning
```

---

## 📚 Further Reading

- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Instruction Tuning Best Practices](https://arxiv.org/abs/2109.01652)
- [Hugging Face Training Guide](https://huggingface.co/docs/transformers/training)
- [AdamW Paper](https://arxiv.org/abs/1711.05101)

---

**Generated**: January 12, 2026
**Script Version**: Fine-Tune v1.0
**Author**: MITRE ATT&CK Classification Project
