"""
ML Model Service - Handles model loading and inference.
"""
import torch
import json
import re
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList
from typing import Dict, Tuple
from loguru import logger
from app.config import settings

# Enable verbose logging for HuggingFace downloads
os.environ['TRANSFORMERS_VERBOSITY'] = 'info'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'


class ReasonCompleteStopper(StoppingCriteria):
    """
    Custom stopping criterion that stops generation after a complete response.
    Stops when we see "Status:" followed by "Reason:" and some text.
    """
    def __init__(self, tokenizer, prompt_length):
        self.tokenizer = tokenizer
        self.prompt_length = prompt_length  # Track where prompt ends
        
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        # Decode ONLY the newly generated tokens (not the prompt)
        generated_tokens = input_ids[0][self.prompt_length:]
        generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        # Check if we have a complete response: Status + Reason with some content
        # We look for "Reason:" followed by at least 20 characters (to ensure it's not cut mid-sentence)
        if "Status:" in generated_text and "Reason:" in generated_text:
            reason_idx = generated_text.rfind("Reason:")
            text_after_reason = generated_text[reason_idx + len("Reason:"):].strip()
            
            # Stop if we have at least 30 characters after "Reason:" (a complete sentence)
            if len(text_after_reason) >= 30:
                # Also check if we hit any conversational markers
                stop_markers = ["Human:", "Please", "I want", "Could you", "Thank"]
                if any(marker in generated_text[reason_idx:] for marker in stop_markers):
                    return True  # Stop immediately if we see conversational text
                
                # Or stop if we have a sentence ending (., !, ?)
                if any(punct in text_after_reason for punct in ['.', '!', '?']):
                    return True
        
        return False


class MLService:
    """Service for ML model operations."""
    
    def __init__(self):
        """Initialize ML service."""
        self.model = None
        self.tokenizer = None
        self.device = settings.DEVICE if torch.cuda.is_available() else "cpu"
        self._model_loaded = False
    
    async def load_model(self):
        """Load the fine-tuned model and tokenizer."""
        if self._model_loaded:
            logger.info("Model already loaded")
            return
        
        try:
            logger.info(f"Loading fine-tuned model from {settings.MODEL_PATH}")
            logger.info(f"Using device: {self.device}")
            
            # ============================================================
            # MATCHING METRICS NOTEBOOK EXACTLY (SINGLE-STEP LOADING)
            # ============================================================
            # Modern transformers library automatically:
            # 1. Detects adapter_config.json in the folder
            # 2. Loads the base model specified in adapter_config.json
            # 3. Applies the LoRA adapters automatically
            # No need for separate base model + PeftModel loading!
            # ============================================================
            
            logger.info("📥 Loading model (auto-detects and applies adapters)...")
            logger.info("   transformers will automatically:")
            logger.info("   1. Load base model: Qwen/Qwen2.5-1.5B-Instruct")
            logger.info("   2. Detect adapter_config.json")
            logger.info("   3. Apply LoRA adapters")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_PATH,  # fine_tuned_model folder with adapters
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            self.model.eval()
            
            logger.success("✅ Fine-tuned model loaded (base + adapters auto-merged)!")
            
            # Load tokenizer FROM FINE-TUNED MODEL PATH (matching metrics notebook)
            logger.info(f"🔤 Loading tokenizer from: {settings.MODEL_PATH}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_PATH,
                trust_remote_code=True
            )
            # Set pad token (transformers default)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            logger.success("✅ Tokenizer loaded!")
            logger.info(f"   EOS token: {self.tokenizer.eos_token}")
            
            self._model_loaded = True
            logger.success("🎉 Model loaded successfully (FP16, no quantization)!")
            logger.info(f"💾 Memory usage: ~3GB GPU RAM")
            
            if self.device == "cuda":
                memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
                current_mem = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"🎮 GPU: {torch.cuda.get_device_name(0)} ({memory_gb:.1f}GB total)")
                logger.info(f"📊 Current GPU usage: {current_mem:.2f}GB")
                
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def _format_prompt(self, log_input: str) -> str:
        """
        Format logs using FEW-SHOT PROMPTING from metrics.ipynb.
        
        CRITICAL: This matches the exact approach used in metrics.ipynb that achieved 70%+ F1 score.
        The few-shot examples guide the model to output the correct format.
        
        Args:
            log_input: Raw log content (JSON string)
            
        Returns:
            Formatted few-shot prompt matching metrics.ipynb
        """
        # Truncate if too long (matching metrics notebook: 6000 chars)
        if len(log_input) > settings.MAX_INPUT_CHARS:
            log_input = log_input[:settings.MAX_INPUT_CHARS] + "... [truncated]"
        
        # FEW-SHOT PROMPT from metrics.ipynb (Cell 8) - THIS IS WHAT WORKED
        # HEAVILY WEIGHTED TOWARD NORMAL (reflects reality: 95%+ of logs are benign)
        prompt = f"""You are a cybersecurity analyst. Analyze system logs and determine if they show normal or suspicious activity.

CRITICAL GUIDELINES:
- 95% of logs are Normal business operations
- Only mark Suspicious if MULTIPLE strong indicators of malicious activity
- Network connections, process executions, file access are usually Normal
- System services, browsers, legitimate apps are Normal
- Be VERY conservative - false positives are worse than missing edge cases

Output format (be concise):
Status: Normal OR Status: Suspicious
MITRE Techniques: T#### (Name), T#### (Name)  <- ONLY if Status is Suspicious
Reason: Brief explanation (1-2 sentences max)

### Example 1 (Normal):
Input: {{"EventID": 4624, "LogonType": 2, "Account": "user@domain.com", "Workstation": "DESKTOP-123"}}
Response:
Status: Normal
Reason: Standard interactive logon from legitimate user account. No suspicious indicators.

### Example 2 (Normal):
Input: {{"EventID": 3, "Protocol": "TCP", "SourceIP": "192.168.1.50", "DestIP": "52.96.144.82", "DestPort": "443", "ProcessName": "chrome.exe"}}
Response:
Status: Normal
Reason: HTTPS connection from Chrome browser. Legitimate web traffic.

### Example 3 (Normal):
Input: {{"EventID": 4688, "Process": "notepad.exe", "CommandLine": "notepad.exe C:\\\\Users\\\\john\\\\Documents\\\\notes.txt", "User": "john"}}
Response:
Status: Normal
Reason: User launching Notepad. Standard application usage.

### Example 4 (Normal):
Input: {{"EventID": 3, "Protocol": "TCP", "DestIP": "147.185.221.22", "DestPort": "443", "ProcessName": "Teams.exe"}}
Response:
Status: Normal
Reason: Outbound connection from Teams application. Legitimate business communication.

### Example 5 (Normal):
Input: {{"EventID": 4688, "Process": "powershell.exe", "CommandLine": "powershell.exe -File startup.ps1", "User": "admin"}}
Response:
Status: Normal
Reason: Administrator running PowerShell script. Routine administrative task.

### Example 6 (Suspicious):
Input: {{"EventID": 4688, "Process": "powershell.exe", "CommandLine": "powershell -enc Base64EncodedCommand -ExecutionPolicy Bypass", "User": "SYSTEM", "ParentProcess": "cmd.exe"}}
Response:
Status: Suspicious
MITRE Techniques: T1059.001 (PowerShell), T1027 (Obfuscated Files)
Reason: Base64-encoded PowerShell with execution policy bypass under SYSTEM account. Strong indicators of malicious automation.

### Now analyze this log:
Input: {log_input}
Response:
"""
        
        return prompt
    
    def _parse_output(self, output: str) -> Dict[str, any]:
        """
        Parse model output matching EXACT training format.
        
        Expected format:
        Status: Normal
        OR
        Status: Suspicious
        MITRE Techniques: T1234, T5678 (Description)
        Reason: explanation
        
        Args:
            output: Raw model output
            
        Returns:
            Dictionary with parsed results
        """
        result = {
            "status": "Normal",  # Default to Normal (most logs are normal)
            "reason": "",
            "mitre_techniques": [],
            "raw_output": output
        }
        
        output_clean = output.strip()
        
        # LOG: Raw model output
        logger.info("=" * 80)
        logger.info("RAW MODEL OUTPUT:")
        logger.info(output_clean)
        logger.info(f"Output length: {len(output_clean)} characters")
        logger.info("=" * 80)
        
        # Parse status - EXACT training format: "Status: Normal" or "Status: Suspicious"
        status_match = re.search(r'Status:\s*(Normal|Suspicious)', output_clean, re.IGNORECASE)
        if status_match:
            status_value = status_match.group(1).lower()
            result["status"] = "Normal" if "normal" in status_value else "Suspicious"
            logger.info(f"Parsed status: {result['status']}")
        
        # Extract MITRE Techniques line (only present for suspicious logs in training data)
        # Format: "MITRE Techniques: T1234 (Name), T5678 (Name)"
        mitre_line_match = re.search(r'MITRE Techniques?:\s*([^\n]+)', output_clean, re.IGNORECASE)
        if mitre_line_match:
            mitre_line = mitre_line_match.group(1)
            # Extract all T#### patterns from the line
            result["mitre_techniques"] = list(set(re.findall(r'T\d{4}(?:\.\d{3})?', mitre_line)))
            logger.info(f"Found MITRE Techniques line: {result['mitre_techniques']}")
        else:
            # FALLBACK: Extract T#### patterns from anywhere in the output
            # This handles cases where model mentions techniques in reason but not in separate line
            all_techniques = list(set(re.findall(r'T\d{4}(?:\.\d{3})?', output_clean)))
            if all_techniques:
                result["mitre_techniques"] = all_techniques
                logger.warning(f"No explicit MITRE Techniques line, extracted from text: {all_techniques}")
        
        # If we found MITRE techniques but status wasn't set, it must be suspicious
        if result["mitre_techniques"] and result["status"] == "Normal":
            result["status"] = "Suspicious"
            logger.warning("Found techniques but status was Normal - overriding to Suspicious")
        
        # Warn if suspicious but no techniques found
        if result["status"] == "Suspicious" and not result["mitre_techniques"]:
            logger.warning("⚠️ Status is Suspicious but NO MITRE techniques found!")
        
        # Extract reason - comes after "Reason:" 
        reason_match = re.search(r'Reason:\s*(.+)', output_clean, re.DOTALL | re.IGNORECASE)
        if reason_match:
            reason_text = reason_match.group(1).strip()
            # Take everything (no truncation - let frontend handle display)
            result["reason"] = reason_text
            logger.info(f"Parsed reason (length={len(reason_text)}): {reason_text[:200]}...")
        
        # Fallback: if we still don't have a reason, use some default text
        if not result["reason"]:
            if result["status"] == "Normal":
                result["reason"] = "Standard system activity with no suspicious indicators"
            else:
                result["reason"] = "Suspicious activity detected"
            logger.warning(f"No reason found, using fallback: {result['reason']}")
        
        # LOG: MITRE techniques found
        if result["mitre_techniques"]:
            logger.info(f"Parsed MITRE techniques: {result['mitre_techniques']}")
        else:
            logger.info("No MITRE techniques found")
        
        # LOG: Final parsed result
        logger.info("PARSED RESULT:")
        logger.info(f"  Status: {result['status']}")
        logger.info(f"  MITRE Techniques: {result['mitre_techniques']}")
        logger.info(f"  Reason length: {len(result['reason'])} chars")
        logger.info(f"  Full reason: {result['reason']}")
        logger.info("=" * 80)
        
        return result
    
    async def analyze_log(self, log_content: str) -> Tuple[str, str, list, str, str]:
        """
        Analyze a log chunk and return classification results.
        
        Args:
            log_content: Log content as string (JSON format expected)
            
        Returns:
            Tuple of (status, reason, mitre_techniques, raw_output, error_message)
        """
        if not self._model_loaded:
            return "Error", "Model not loaded", [], "", "Model not initialized. Please wait for model loading."
        
        try:
            # Validate JSON if it looks like JSON
            if log_content.strip().startswith('{') or log_content.strip().startswith('['):
                try:
                    json.loads(log_content)
                except json.JSONDecodeError as e:
                    return "Error", f"Invalid JSON: {str(e)}", [], "", str(e)
            
            # Format prompt
            prompt = self._format_prompt(log_content)
            
            logger.info("=" * 80)
            logger.info("PROMPT FORMAT CHECK:")
            logger.info(f"Prompt length: {len(prompt)} chars")
            logger.info(f"First 200 chars: {prompt[:200]}")
            logger.info(f"Last 100 chars: {prompt[-100:]}")
            logger.info("=" * 80)
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=settings.MAX_LENGTH_TOKENS
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate with sampling (EXACT MATCH TO NOTEBOOK EVALUATION)
            logger.info("Generating prediction...")
            logger.info(f"Settings: temp={settings.TEMPERATURE}, top_p={settings.TOP_P}, max_tokens={settings.MAX_NEW_TOKENS}")
            
            # Use tokenizer's default EOS token (don't override)
            logger.info(f"Using default EOS token ID: {self.tokenizer.eos_token_id} ({self.tokenizer.eos_token})")
            
            # Create custom stopping criterion to prevent hallucination
            # Pass prompt length so it only checks newly generated tokens, not the examples in the prompt
            prompt_length = inputs['input_ids'].shape[1]
            stopping_criteria = StoppingCriteriaList([ReasonCompleteStopper(self.tokenizer, prompt_length)])
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.MAX_NEW_TOKENS,
                    temperature=settings.TEMPERATURE,  # Low temp for conservative classification
                    do_sample=True,  # Enable sampling
                    top_p=settings.TOP_P,  # Nucleus sampling
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,  # Use tokenizer's default
                    stopping_criteria=stopping_criteria,  # Stop as soon as response is complete
                    repetition_penalty=1.1  # Discourage repetitive rambling
                )
            
            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            logger.info(f"Generated {len(generated_text)} characters (before cleanup)")
            
            # Post-process: Remove conversational follow-ups and unwanted continuations
            # The model sometimes continues generating after the Reason, adding conversational text
            # Be VERY aggressive with stopping patterns
            stopping_patterns = [
                "\n\nPlease",           # Any "Please" continuation
                "\n\nHuman:",           # Chat-style continuation
                "\n\nAssistant:",       # Chat-style continuation  
                "\n\nInput:",           # Trying to analyze another log
                "\n\n### Example",      # Trying to give more examples
                "\n\nCan you",          # Asking follow-up questions
                "\n\nNote:",            # Additional notes
                "\n\n###",              # New section markers
                "\n\n---",              # Separator lines
                "\n\nI ",               # First-person continuation
                "\n\nThe analysis",     # Meta-commentary
                "\nHuman:",             # Single newline variant
                "\nAssistant:",         # Single newline variant
                "Human:",               # No newline at all
                "Assistant:",           # No newline at all
                "\nPlease provide",     # Asking for more details
                "\nI want to",          # Conversational continuation
                "\nFor example,",       # Providing examples
                "\nThank you",          # Polite endings
                "\nCould you",          # Questions
                "\nWould you",          # Questions
            ]
            
            original_length = len(generated_text)
            for pattern in stopping_patterns:
                if pattern in generated_text:
                    generated_text = generated_text.split(pattern)[0]
                    logger.info(f"✂️ Trimmed at '{pattern}': {original_length} -> {len(generated_text)} chars")
                    break
            
            # Additional aggressive trimming: if we see anything that looks like a question or continuation
            # after "Reason:", cut it off
            lines = generated_text.split('\n')
            clean_lines = []
            found_reason = False
            
            for line in lines:
                clean_lines.append(line)
                if line.strip().startswith('Reason:'):
                    found_reason = True
                # After finding Reason, stop at any line that looks conversational
                elif found_reason and line.strip():
                    # Check if this line looks like conversational continuation
                    lower_line = line.lower().strip()
                    if any(lower_line.startswith(phrase) for phrase in [
                        'please', 'human:', 'assistant:', 'i want', 'could you', 
                        'would you', 'for example', 'thank you', 'can you'
                    ]):
                        clean_lines.pop()  # Remove this line
                        logger.info(f"✂️ Removed conversational line after Reason: '{line[:50]}...'")
                        break
            
            generated_text = '\n'.join(clean_lines).rstrip()
            
            # ABSOLUTE FAILSAFE: Hard character limit (Status + Techniques + Reason should be < 300 chars)
            MAX_CHARS = 300
            if len(generated_text) > MAX_CHARS:
                logger.warning(f"⚠️ Output too long ({len(generated_text)} chars), truncating to {MAX_CHARS}")
                # Cut at last complete sentence (., !, ?)
                truncated = generated_text[:MAX_CHARS]
                last_sentence_end = max(
                    truncated.rfind('.'),
                    truncated.rfind('!'),
                    truncated.rfind('?')
                )
                if last_sentence_end > 0:
                    generated_text = truncated[:last_sentence_end + 1]
                else:
                    generated_text = truncated.rsplit('\n', 1)[0]  # Fall back to last complete line
            
            logger.info(f"Final output: {len(generated_text)} characters")
            
            # Parse output
            result = self._parse_output(generated_text)
            
            return (
                result["status"],
                result["reason"],
                result["mitre_techniques"],
                result["raw_output"],
                ""  # No error
            )
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return "Error", f"Analysis failed: {str(e)}", [], "", str(e)
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model_loaded


# Global ML service instance
ml_service = MLService()
