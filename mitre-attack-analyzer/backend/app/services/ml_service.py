"""
ML Model Service - Handles model loading and inference.
"""
import torch
import json
import re
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from typing import Dict, Tuple
from loguru import logger
from app.config import settings

# Enable verbose logging for HuggingFace downloads
os.environ['TRANSFORMERS_VERBOSITY'] = 'info'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'


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
            logger.info(f"Loading model from {settings.MODEL_PATH}")
            logger.info(f"Using device: {self.device}")
            
            # Load base model
            logger.info(f"Loading base model: {settings.BASE_MODEL}")
            logger.info("📥 Using 8-bit quantization to reduce memory usage...")
            logger.info("This fits the 3GB model into ~1.5GB RAM (works on systems with low memory)")
            
            # Configure 8-bit quantization
            bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.float16
            )
            
            base_model = AutoModelForCausalLM.from_pretrained(
                settings.BASE_MODEL,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )
            logger.success("✅ Base model loaded with 8-bit quantization!")
            
            # Load LoRA adapters
            logger.info(f"📦 Loading LoRA adapters from: {settings.MODEL_PATH}")
            self.model = PeftModel.from_pretrained(base_model, settings.MODEL_PATH)
            self.model.eval()
            logger.success("✅ LoRA adapters loaded!")
            
            # Load tokenizer
            logger.info("🔤 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.BASE_MODEL,
                trust_remote_code=True
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token
            logger.success("✅ Tokenizer loaded!")
            
            self._model_loaded = True
            logger.success("🎉 Model loaded successfully with 8-bit quantization!")
            logger.info(f"💾 Memory savings: ~50% (3GB → 1.5GB)")
            
            if self.device == "cuda":
                memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"🎮 GPU: {torch.cuda.get_device_name(0)} ({memory_gb:.1f}GB)")
                
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def _format_prompt(self, log_input: str) -> str:
        """
        Format logs using chat template matching EXACT training format.
        
        Args:
            log_input: Raw log content (JSON string)
            
        Returns:
            Formatted prompt string with chat template
        """
        # Truncate if too long
        if len(log_input) > settings.MAX_INPUT_CHARS:
            log_input = log_input[:settings.MAX_INPUT_CHARS] + "... [truncated]"
        
        # EXACT instruction from training data
        instruction = "Analyze this session log chunk and determine if it contains normal or suspicious activity. If suspicious, identify all MITRE ATT&CK techniques and explain why."
        
        # Combine instruction + input (matching training format)
        user_message = f"{instruction}\n\n{log_input}"
        
        # Apply chat template (Qwen format)
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        # Use tokenizer's chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
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
        
        # Parse status - EXACT training format: "Status: Normal" or "Status: Suspicious"
        status_match = re.search(r'Status:\s*(Normal|Suspicious)', output_clean, re.IGNORECASE)
        if status_match:
            status_value = status_match.group(1).lower()
            result["status"] = "Normal" if "normal" in status_value else "Suspicious"
        
        # Extract MITRE Techniques line (only present for suspicious logs in training data)
        # Format: "MITRE Techniques: T1234 (Name), T5678 (Name)"
        mitre_line_match = re.search(r'MITRE Techniques?:\s*([^\n]+)', output_clean, re.IGNORECASE)
        if mitre_line_match:
            mitre_line = mitre_line_match.group(1)
            # Extract all T#### patterns from the line
            result["mitre_techniques"] = list(set(re.findall(r'T\d{4}(?:\.\d{3})?', mitre_line)))
            # If we found MITRE techniques but status wasn't set, it must be suspicious
            if result["mitre_techniques"] and result["status"] == "Normal":
                result["status"] = "Suspicious"
        
        # Extract reason - comes after "Reason:" 
        reason_match = re.search(r'Reason:\s*(.+)', output_clean, re.DOTALL | re.IGNORECASE)
        if reason_match:
            reason_text = reason_match.group(1).strip()
            # Take everything up to end or next section
            result["reason"] = reason_text[:500]
        
        # Fallback: if we still don't have a reason, use some default text
        if not result["reason"]:
            if result["status"] == "Normal":
                result["reason"] = "Standard system activity with no suspicious indicators"
            else:
                result["reason"] = "Suspicious activity detected"
        
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
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=settings.MAX_LENGTH_TOKENS
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate with greedy decoding for consistent classification
            logger.info("Generating prediction...")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.MAX_NEW_TOKENS,
                    do_sample=False,  # Greedy decoding for classification
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            logger.info(f"Generated {len(generated_text)} characters")
            
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
