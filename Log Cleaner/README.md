# Log Cleaner and Uploader

This tool automatically downloads logs from Google Drive, cleans and processes them, then uploads the cleaned data back to Google Drive in an organized structure.

## Project Structure

```
Log Cleaner/
├── main.py                 # Main entry point
├── gdrive_helper.py        # Google Drive operations
├── log_parser.py           # Log parsing functions
├── .env                    # Configuration
├── credentials.json        # Google Drive credentials
└── requirements.txt        # Dependencies
```

## Features

- **Automated Download:** Fetches the most recent N log sessions from Google Drive
- **Parse Multiple Log Types:**
  - System logs (JSON/JSONL format from Kibana)
  - Browser activity logs (ActivityWatch JSON format)
  - Network packets (PCAP format)

- **Data Cleaning:**
  - Removes duplicate entries
  - Standardizes timestamps
  - Anonymizes sensitive information (host names, agent IDs)
  - Sorts events chronologically
  - Merges all log types into a single JSON file

- **Google Drive Integration:**
  - Downloads from `Mitre-Dataset-Monitoring` folder
  - Uploads cleaned data to `Cleaned_Logs` subfolder
  - Creates organized folder structure with timestamps

- **Automatic Cleanup:** Deletes temporary files after processing

## Workflow

```
Google Drive (Raw Logs)
    ↓ Download
Local Processing
    ↓ Clean & Merge
Google Drive (Cleaned Logs)
    ↓ Auto-delete local temp files
Clean System
```

## Prerequisites

1. Python 3.7 or higher
2. Required packages (install via pip):
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup credentials and environment:**
   - Copy `.env.example` to `.env`
   - Edit `.env` to configure:
     - `GDRIVE_FOLDER_NAME`: Your main Google Drive folder name
     - `NUM_SESSIONS_TO_PROCESS`: How many recent sessions to process (default: 5)
   - Place your `credentials.json` file in this folder (get it from Google Cloud Console)
   - On first run, you'll be prompted to authenticate with Google Drive

## Usage

### Simple Command

Just run the main script:

```bash
python main.py
```

The script will automatically:
1. Connect to your Google Drive
2. Find the last N sessions (configured in `.env`)
3. Download all log files from each session
4. Clean and merge the logs
5. Upload cleaned data to `Cleaned_Logs` folder with **original timestamps**
6. Delete all temporary local files

### Configuration

Edit `.env` file:

```env
# Main Google Drive folder containing raw logs
GDRIVE_FOLDER_NAME=Mitre-Dataset-Monitoring

# Subfolder for text logs
GDRIVE_CLEANED_LOGS_FOLDER=Text_Logs

# Number of recent sessions to process
NUM_SESSIONS_TO_PROCESS=5
```

## Output

### Google Drive Structure

```
My Drive/
├── Mitre-Dataset-Monitoring/     # Raw logs folder
│   ├── 20251101_101300/
│   │   ├── syslogs_*.json
│   │   ├── packet_capture_*.pcap
│   │   ├── aw-watcher-*.json
│   │   └── screen_record_*.avi (skipped)
│   └── 20251101_094500/
│       └── ...
│
└── Text_Logs/                     # Separate text logs folder
    ├── 20251101_101300/
    │   └── text_log_20251101_101300.json
    └── 20251101_094500/
        └── text_log_20251101_094500.json
```

### Output Format

The cleaned logs are saved as a JSON array with standardized event objects:

```json
[
  {
    "timestamp": "2025-10-25T15:46:00.000000",
    "event_type": "browser",
    "url": "https://example.com",
    "title": "Example Page",
    "duration": 5.2
  },
  {
    "timestamp": "2025-10-25T15:46:01.000000",
    "event_type": "system",
    "process_name": "chrome.exe",
    "command_line": "...",
    "host_id": "a1b2c3d4"
  },
  {
    "timestamp": "2025-10-25T15:46:02.000000",
    "event_type": "network",
    "protocol": "TCP",
    "src_ip": "192.168.1.100",
    "dst_ip": "93.184.216.34",
    "src_port": 54321,
    "dst_port": 443
  }
]
```

## Notes

- PCAP parsing requires `pyshark` and `Wireshark/tshark` to be installed
- System logs must be in JSONL format (one JSON object per line)
- Browser logs must be in ActivityWatch JSON format
- All sensitive information (hostnames, agent IDs) are automatically anonymized using MD5 hashing
