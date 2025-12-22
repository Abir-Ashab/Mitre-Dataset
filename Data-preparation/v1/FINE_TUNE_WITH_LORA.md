# Fine-tuning with LoRA (session-aware training data)

## Training data format

- File format: JSONL (one JSON object per line).
- Each example is an instruction-tuning record with the following keys:
  - `instruction`: A short natural-language instruction for the model. Example: "Analyze this session log chunk and determine if it contains normal or suspicious activity. If suspicious, identify all MITRE ATT&CK techniques and explain why."
  - `input`: A JSON string containing:
    - `metadata`: object with `session_id`, `start_time`, `end_time`, `number_of_events`.
    - `logs`: an array of raw log objects (preserve ALL original fields, do NOT flatten or summarize).
      Example structure (as JSON inside the `input` string):
      {
      "metadata": {"session_id": "20251025_184200", "start_time": "2025-10-25T12:42:18.139Z", "end_time": "2025-10-25T12:42:58.867Z", "number_of_events": 30},
      "logs": [ { ... full log object ... }, { ... }, ... ]
      }
  - `output`: Text the model should produce. Use a small structured response, for example:
    - `Status: Suspicious` or `Status: Normal`
    - If suspicious: `MITRE Techniques: T1071.001 (Application Layer Protocol: Web Protocols), T1041 (Exfiltration Over C2 Channel)`
    - `Reason: ...` short explanation referencing behavioral indicators

Notes:

- Keep every original field from logs; only remove the `label` and `mitre_techniques` fields from the `input` logs (these are used to construct `output`).
- Examples are session-chunked: each JSONL example represents a contiguous chunk of N logs from the same `session_id` (e.g., 20–50 logs or fixed time window).
- Train/Val/Test splits are done by SESSION (all chunks of one session remain in the same split) to avoid leakage.

---

# Fine-Tuning Steps (LoRA)

## 1. Choose a model

Recommended for an 8GB GPU:

- Qwen 2.5 1.5B (good balance of performance and memory)
- Llama 3.2 3B (better accuracy, higher memory needs)

## 2. Install dependencies

```bash
pip install transformers datasets torch accelerate peft trl bitsandbytes
```

## 3. Fine-tuning script (`fine_tune_lora.py`)

Create `fine_tune_lora.py` under the `Data-Extraction-Training-format` folder with the following content:

```python
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset

# Format instruction into a single text field for tokenization
def format_instruction(example):
    return {
        "text": f"<|im_start|>user\n{example['instruction']}\n\nInput: {example['input']}<|im_end|>\n<|im_start|>assistant\n{example['output']}<|im_end|>"
    }


def main():
    MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"  # or another compatible causal LM
    OUTPUT_DIR = "./fine_tuned_model"

    # Load model with 4-bit quantization (QLoRA style)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        load_in_4bit=True,
        device_map="auto"
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    # Prepare model for k-bit training and apply LoRA
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset('json', data_files={'train': 'training_data/train.jsonl', 'validation': 'training_data/val.jsonl'})
    dataset = dataset.map(format_instruction)

    def tokenize_function(examples):
        return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=1024)

    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset['train'].column_names)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        weight_decay=0.01,
        warmup_steps=100,
        logging_steps=10,
        save_steps=500,
        evaluation_strategy="steps",
        eval_steps=500,
        save_total_limit=2,
        load_best_model_at_end=True,
        fp16=True
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset['train'],
        eval_dataset=tokenized_dataset['validation']
    )

    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

if __name__ == '__main__':
    main()
```

## 4. Run fine-tuning

```bash
cd E:\Hacking\Mitre-Dataset\Data-Extraction-Training-format
python fine_tune_lora.py
```

Notes:

- Adjust `per_device_train_batch_size` and `gradient_accumulation_steps` to fit VRAM.
- Monitor GPU memory; reduce `max_length` or batch size if OOM occurs.

## 5. Quick test script (`test_model.py`)

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = "Qwen/Qwen2.5-1.5B-Instruct"

base_model = AutoModelForCausalLM.from_pretrained(base)
 tokenizer = AutoTokenizer.from_pretrained(base)
model = PeftModel.from_pretrained(base_model, "./fine_tuned_model")

test_input = """Analyze this session log chunk and determine if it contains normal or suspicious activity.\n\nInput: {\"metadata\": {\"session_id\": \"example\", \"start_time\": \"2025-10-25T12:42:18Z\", \"end_time\": \"2025-10-25T12:42:58Z\", \"number_of_events\": 30}, \"logs\": [ /* full logs here */ ] }"""

inputs = tokenizer(test_input, return_tensors='pt').to(model.device)
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.1)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## 6. Evaluate on test set (`evaluate_model.py`)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import json

base = "Qwen/Qwen2.5-1.5B-Instruct"
base_model = AutoModelForCausalLM.from_pretrained(base)
 tokenier = AutoTokenizer.from_pretrained(base)
model = PeftModel.from_pretrained(base_model, "./fine_tuned_model")

# Load test examples
with open('training_data/test.jsonl', 'r') as f:
    test_examples = [json.loads(line) for line in f]

# Simple binary check on a subset
correct = 0
for ex in test_examples[:50]:
    input_text = f"{ex['instruction']}\n\nInput: {ex['input']}"
    inputs = tokenizer(input_text, return_tensors='pt').to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.1)
    pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if ('Suspicious' in ex['output'] and 'Suspicious' in pred) or ('Normal' in ex['output'] and 'Normal' in pred):
        correct += 1

print(f"Accuracy on sample: {correct}/50 = {correct/50*100:.1f}%")
```

## 7. Deployment (load LoRA adapter)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = "Qwen/Qwen2.5-1.5B-Instruct"
base_model = AutoModelForCausalLM.from_pretrained(base)
tokenizer = AutoTokenizer.from_pretrained(base)
model = PeftModel.from_pretrained(base_model, "./fine_tuned_model")

# Use model for inference as usual
```

---

## Tips & Troubleshooting

- If you get OOM errors: reduce `per_device_train_batch_size`, reduce `max_length`, or increase `gradient_accumulation_steps`.
- Keep `training_data` splits by session to avoid leakage.
- Monitor validation loss and use `load_best_model_at_end=True` to save the best adapter.

---

File created: `Data-Extraction-Training-format/FINE_TUNE_WITH_LORA.md`
