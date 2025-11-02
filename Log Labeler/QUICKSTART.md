# Quick Start - Gemini AI Setup

## 3 Steps to Get Started

### Step 1: Get API Key (2 minutes)
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Step 2: Add to .env File
```bash
# Edit this file: e:\Hacking\Mitre-Dataset\Log Labeler\.env
GEMINI_API_KEY=paste_your_key_here
```

### Step 3: Run
```bash
cd "e:\Hacking\Mitre-Dataset\Log Labeler"
python main.py
```

That's it! 🎉

## What You'll See

```
Processing session 20251101_134100...
✓ Downloaded 3 log files
✓ Analyzing with Gemini AI...
  - Event 1: suspicious (T1059.001) - PowerShell execution
  - Event 2: normal - Regular browser activity  
  - Event 3: suspicious (T1041, T1567.002) - Data exfiltration
✓ Uploaded to Labeled_Logs/20251101_134100/
Done!
```

## Benefits

✅ **Intelligent Detection**: AI understands context, not just keywords
✅ **Explains Reasoning**: Know why each event is labeled
✅ **Free**: 60 requests/minute, no credit card
✅ **Fallback Safe**: Works even if API fails

## Need Help?

See full documentation: `README.md` or `GEMINI_SETUP.md`
