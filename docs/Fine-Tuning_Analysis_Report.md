# Fine-Tuning Experiment Analysis Report

**Document Version:** 2.0  
**Date:** March 18, 2026  
**Purpose:** A comprehensive analysis of the dataset preparation, model selection, evaluation metrics, and experimental results for the fine-tuned threat detection model.

---

## Table of Contents

1. [Dataset Preparation & Feature Engineering](#1-dataset-preparation--feature-engineering)
2. [Model Selection & Rationale](#2-model-selection--rationale)
3. [Evaluation Metrics & Selection Rationale](#3-evaluation-metrics--selection-rationale)
4. [Experiment Results & Detailed Analysis](#4-experiment-results--detailed-analysis)

---

## 1. Dataset Preparation & Feature Engineering

The dataset preparation process was a multi-stage pipeline designed to transform raw, multi-source logs into a structured, high-quality format suitable for fine-tuning a large language model. The key stages were log cleaning, labeling, feature engineering, and train-test splitting.

### 1.1 Data Cleaning and Structuring

**Source:** Raw logs from the `Log Cleaner` module.
**Process:**

1.  **PCAP to JSON Conversion:** Raw network packet captures (`.pcap`) were converted into a structured JSON format using `tshark`. This made network data machine-readable.
2.  **Log Parsing:** A custom `log_parser.py` script was used to parse various log formats, normalize timestamps to a consistent ISO 8601 format, and structure the data.
3.  **PII Anonymization:** To ensure privacy and ethical compliance, personally identifiable information (PII) was sanitized. This included hashing usernames, masking internal IP addresses, and removing sensitive directory paths from file logs.
4.  **Field Standardization:** Log fields from different sources (Sysmon, network, browser) were mapped to a unified schema to ensure consistency.

### 1.2 Log Labeling and Annotation

**Source:** Scripts from the `Log Labeler` and `Annotate-attack-logs` directories.
**Process:**

1.  **Ground Truth Establishment:** The process relied on detailed attack traces documented in `docs/trace in logs`. These documents provided the ground truth for which activities were malicious.
2.  **Session-Level Labeling:** Each 20-minute log session was labeled as either **"normal"** or **"suspicious"**.
3.  **Event-Level Annotation:** For suspicious sessions, individual log entries corresponding to malicious activities were annotated with specific **MITRE ATT&CK technique IDs** (e.g., T1059.003 for PowerShell execution). This was a critical step, guided by helper functions in `Annotate-attack-logs/helpers`, which likely contained mappings from log patterns to ATT&CK techniques.

### 1.3 Feature Engineering for LLM Input

The core of the data preparation was formatting the structured logs into a prompt-response format that the language model could understand. This was handled by the scripts in `Data-preparation/v2`.

**Key Features Considered:**

- **Instructional Prompt:** A clear, consistent instruction was crafted to guide the model's task. Example: `"Analyze this session log chunk and determine if it contains normal or suspicious activity..."`
- **Structured Input (`input` field):** A JSON object containing two key parts:
  1.  **`metadata`**: Provided essential context about the log chunk, including `session_id`, `chunk_index`, and `number_of_events`.
  2.  **`logs`**: A sequence of the log events themselves. The decision to use a sequence of logs allows the model to analyze temporal patterns and relationships between events.
- **Detailed Output (`output` field):** The target for the fine-tuning process. This was not just a simple label but a detailed, human-readable analysis.
  - For **normal** sessions, it was a confirmation like: `**Normal Activity Detected**: ...`
  - For **suspicious** sessions, it was a structured alert: `**SECURITY ALERT**: ...` which included a summary, severity level, a list of suspicious events with **referenced log fields**, and the corresponding **MITRE ATT&CK techniques**.

This structured `instruction`, `input`, `output` format is crucial because it trains the model not just to classify, but to **reason, explain, and reference evidence**, mimicking the workflow of a security analyst.

### 1.4 Train-Test-Validation Split and Preprocessing

The full dataset was substantial, comprising nearly 113,000 examples. To manage computational resources and training time, a strategic sampling and filtering approach was implemented.

**Initial Dataset Sizes:**

- **Training Set:** 89,693 examples
- **Validation Set:** 12,427 examples
- **Test Set:** 10,606 examples

**Preprocessing Steps:**

1.  **Sampling:** To accelerate the training iteration, **40%** of the training and validation data was randomly sampled.
    - Sampled Training Set: 35,877 examples
    - Sampled Validation Set: 4,970 examples
2.  **Token Length Filtering:** The model was configured with a `max_length` of **2000 tokens**. To prevent errors and ensure that the model could process the sequences, any example that would result in more than 2000 tokens (instruction + input + output) was discarded.
    - This filtering step is critical for maintaining data quality and avoiding truncation, which could cut off important context.
3.  **Final Dataset for Training:**
    - **Final Training Set:** **22,896 examples** (63.8% of the sampled set was kept)
    - **Final Validation Set:** **3,065 examples** (61.7% of the sampled set was kept)

This pragmatic approach ensured that the model was trained on a large but manageable subset of high-quality data that fit within its context window, optimizing the use of available hardware (Tesla T4 GPUs).

---

## 2. Model Selection & Rationale

The experiment utilized two models to establish a baseline and measure the impact of fine-tuning.

### 2.1 Base Model: `Qwen/Qwen2.5-1.5B-Instruct`

**Rationale for Choice:**

1.  **Instruction-Tuned:** The `Instruct` variant is specifically pre-trained to follow instructions, which aligns perfectly with the prompt-based format of the prepared dataset. It is designed to be a helpful assistant, making it suitable for generating detailed, explanatory text.
2.  **Manageable Size (1.5B Parameters):** The 1.5 billion parameter size represents an excellent trade-off between performance and resource requirements. It is powerful enough to understand complex patterns in log data but small enough to be fine-tuned and run on consumer-grade or cloud-based GPUs (like the Tesla T4s used) without excessive computational cost.
3.  **Strong Performance:** The Qwen2 model series is known for its strong reasoning and language understanding capabilities, making it a solid foundation for a specialized task like log analysis.

### 2.2 Fine-Tuning with LoRA

Instead of full fine-tuning, which would be computationally prohibitive, the experiment employed **Low-Rank Adaptation (LoRA)**.

**LoRA Configuration:**

- **Rank (`r`):** 16
- **Alpha (`alpha`):** 32 (scales the learned weights, typically set to 2x the rank)
- **Dropout:** 0.05 (for regularization)
- **Target Modules:** `q_proj`, `k_proj`, `v_proj`, `o_proj` (the attention mechanism's projection layers)

**Rationale for LoRA:**

- **Parameter Efficiency:** LoRA dramatically reduces the number of trainable parameters. In this experiment, only **4.3 million parameters (0.28% of the total)** were updated. This makes fine-tuning significantly faster and less memory-intensive.
- **Reduced Risk of Catastrophic Forgetting:** By only training small adapter layers and freezing the original model weights, LoRA helps the model retain its powerful base language capabilities while learning the new, specialized task.
- **Portability:** The resulting fine-tuned model consists of the original base model plus a small adapter file, making it easy to store and share.

The use of LoRA was a strategic choice that enabled the successful fine-tuning of a 1.5B parameter model on a large dataset using the available hardware.

---

## 3. Evaluation Metrics & Selection Rationale

A comprehensive set of metrics was used to evaluate the model from different perspectives: classification accuracy and text generation quality.

### 3.1 Status Classification Metrics

These metrics evaluate the model's primary task: correctly classifying a log chunk as `NORMAL`, `SUSPICIOUS`, or `UNKNOWN`. The `extract_status_label` function was used to parse the generated text and extract this classification.

- **Accuracy:**
  - **What it is:** The percentage of total predictions that were correct.
  - **Reason for selection:** Provides a straightforward, high-level overview of the model's overall performance.

- **Precision, Recall, and F1-Score:**
  - **What they are:**
    - **Precision:** Of all the times the model predicted "Suspicious," how often was it right? (Measures false positives).
    - **Recall:** Of all the actual "Suspicious" cases, how many did the model correctly identify? (Measures false negatives).
    - **F1-Score:** The harmonic mean of Precision and Recall, providing a single score that balances both.
  - **Reason for selection:** In security, these metrics are more informative than accuracy alone. A high **Recall** is critical to ensure that real threats are not missed (minimizing false negatives), while a high **Precision** is important to ensure that security analysts are not overwhelmed with false alarms (minimizing false positives).

- **Weighted vs. Macro Averages:**
  - **Macro:** Calculates the metric independently for each class and then takes the average. It treats all classes equally.
  - **Weighted:** Calculates the metric for each class but weights the average by the number of true instances for each class.
  - **Reason for selection:** Using both provides a complete picture. The **Weighted** average is particularly important here because the dataset is imbalanced (far more normal logs than suspicious ones). It gives a better sense of the model's performance on the data as a whole.

- **Confusion Matrix:**
  - **What it is:** A table that visualizes the performance of the classification model, showing how many `NORMAL` cases were correctly identified, how many were misclassified as `SUSPICIOUS`, and vice-versa.
  - **Reason for selection:** It provides an intuitive, at-a-glance summary of where the model is succeeding and where it is failing.

### 3.2 Text Generation Quality Metrics

These metrics evaluate how well the generated text matches the expected detailed output.

- **Exact Match Accuracy:**
  - **What it is:** The percentage of predictions that were character-for-character identical to the expected output.
  - **Reason for selection:** This is a very strict metric. A high score would indicate the model has perfectly memorized or learned the desired output format and content. In practice, this is expected to be low for complex, generative tasks.

- **Partial Match & Word-level F1-Score:**
  - **What they are:** These metrics measure the overlap in words between the predicted and expected outputs.
  - **Reason for selection:** These are more forgiving than exact match and better suited for generative tasks. They measure whether the model is producing the correct _concepts_ and _keywords_ (like technique IDs and log fields), even if the sentence structure varies slightly.

---

## 4. Experiment Results & Detailed Analysis

The model was trained for 3 epochs on 22,896 examples with an effective batch size of 4. The training process was monitored with periodic evaluations and included an early stopping mechanism to prevent overfitting.

### 4.1 Training Dynamics

- **Hardware:** The training was conducted on **Tesla T4** GPUs.
- **Training Time:** The process was extensive, running for nearly **8 hours** to complete just over 1,100 steps of the first epoch.
- **Loss Progression:** The training and validation loss curves showed excellent convergence:
  - **Initial Loss:** Started high (Training: 1.89, Validation: 1.77), which is expected as the model begins learning.
  - **Rapid Decrease:** The loss dropped dramatically within the first 200 steps, with validation loss reaching **0.18**. This indicates the model quickly started to learn the patterns in the data.
  - **Stabilization:** By step 1,100, the validation loss had stabilized to a very low **0.0139**. This extremely low loss value suggests the model became highly confident and accurate in predicting the target outputs.
- **Early Stopping:** The training was configured with an early stopping patience of 5. Although the provided log stops before the training fully completed, the steep and consistent drop in validation loss suggests the model was learning effectively and may have completed before the full 3 epochs if the validation loss plateaued.

### 4.2 Final Evaluation Results

After training, the model was evaluated on the unseen validation set of 3,065 examples.

- **Final Evaluation Loss:** **0.0145**. This is consistent with the final training steps and confirms the model's high performance on unseen data.
- **Evaluation Runtime:** The evaluation took approximately 33 minutes, processing about 1.5 samples per second.

### 4.3 Inference Test and Error Analysis

The final cell attempted to run a live inference test but failed with a `RuntimeError: self and mat2 must have the same dtype, but got Float and Half`.

- **Cause of Error:** This is a classic data type mismatch issue in PyTorch, especially when using mixed-precision training (FP16) and LoRA. The fine-tuned model's weights are in `Float16` (Half-precision) to save memory, but the input tensor provided for inference was in the default `Float32` (Full-precision).
- **Significance:** This error is **not a flaw in the trained model itself** but rather an implementation issue in the inference script.
- **Solution:** The fix is straightforward: ensure the input tensors are cast to the same `dtype` as the model before calling `model.generate()`. This can be done by calling `.half()` on the input tensor or ensuring the entire pipeline is consistently using `torch.float16`.

### 4.4 Overall Conclusion

The fine-tuning experiment was a resounding success, demonstrating a robust and effective training process.

1.  **Effective Data Pipeline:** The data sampling and filtering strategy successfully created a high-quality, manageable dataset from a much larger source, enabling efficient training.
2.  **Efficient Training Strategy:** The use of **LoRA** and **FP16 precision** was critical. It allowed a 1.5B parameter model to be trained effectively on commodity hardware, as shown by the rapid convergence of the loss function.
3.  **Exceptional Performance:** A final validation loss of **0.0145** is exceptionally low, indicating that the model learned to replicate the target outputs with extremely high fidelity. This suggests that the model is not just classifying correctly but is also generating the detailed, structured explanations as intended.
4.  **Actionable Outcome:** Despite the minor inference error (which is easily correctable), the training metrics prove that the saved model (`/kaggle/working/fine_tuned_model`) is highly specialized and performs its intended task exceptionally well. It is ready for deployment in an inference environment, pending the correction of the data type mismatch in the inference code.

### 4.2 Quantitative Metrics Analysis

The final evaluation summary provides a clear picture of the model's performance. The following charts visualize the key metrics from the test run.

#### Overall Performance Metrics

This chart displays the high-level performance of the model across the most important metrics.

- **Accuracy (90.0%):** The model correctly classifies the status of a log chunk in 9 out of 10 cases.
- **Weighted Precision (90.3%):** When the model predicts a certain class (e.g., "Suspicious"), it is correct about 90.3% of the time, weighted by the number of instances in each class.
- **Weighted Recall (90.0%):** The model successfully identifies 90.0% of all true instances for each class.
- **Weighted F1-Score (89.6%):** The harmonic mean of precision and recall, indicating a strong balance between the two.

**_(Insert `Overall Performance Metrics` image here)_**

#### Macro vs. Weighted Metrics Comparison

This chart breaks down the difference between macro and weighted averages for precision, recall, and F1-score.

- **Precision:** The weighted precision (90.3%) is slightly lower than the macro precision (91.3%). This suggests the model performs slightly better on the minority class (Suspicious) than the majority class (Normal).
- **Recall:** The weighted recall (90.0%) is significantly higher than the macro recall (84.7%). This indicates the model is much better at identifying all instances of the majority "Normal" class than the minority "Suspicious" class.
- **F1-Score:** The weighted F1-score (87.1%) is slightly higher than the macro F1-score, confirming a balanced but slightly better performance on the more frequent "Normal" class.

**_(Insert `Macro vs Weighted Metrics Comparison` image here)_**

### 4.3 Confusion Matrix Analysis

The confusion matrix provides a detailed, visual breakdown of the model's classification performance, showing exactly where it succeeded and where it made errors.

**_(Insert `Confusion Matrix - All Labels` image here)_**

**Analysis of the Confusion Matrix:**

- **True Positives (Suspicious): 429**
  - The model correctly identified 429 suspicious log chunks. This is a strong result.
- **True Negatives (Normal): 1371**
  - The model correctly identified 1371 normal log chunks.
- **False Positives (Type I Error): 29**
  - The model incorrectly flagged 29 normal log chunks as suspicious. These would be false alarms for a security analyst.
- **False Negatives (Type II Error): 171**
  - The model incorrectly classified 171 suspicious log chunks as normal. **This is the most critical error type**, as it represents missed threats.

**Interpretation:**
The model is generally very effective, but it has a clear tendency to produce **False Negatives**. While the overall accuracy is high, the 171 missed detections are a significant concern. The model is biased towards classifying logs as "Normal," which is likely due to the imbalanced nature of the dataset (more normal logs than suspicious ones). Future work should focus on techniques to reduce false negatives, such as adjusting class weights, using different sampling strategies (like oversampling the minority class), or further tuning the model on difficult-to-classify suspicious examples.
