# Automated Log Extraction and Monitoring with Google Drive Upload

This project provides scripts for extracting system logs, browser logs, monitoring system activity, capturing network packets, and recording the screen. All collected data is automatically uploaded to Google Drive for secure storage and accessibility from anywhere.

## Features
- Extract system logs from Elasticsearch (`extract_syslogs.py`)
- Extract browser logs from ActivityWatch (`extract_browser_logs.py`) 
- Capture network packets using Wireshark (`packet_capture.py`)
- Record screen activity (`screen_recorder.py`)
- Automatic upload to Google Drive (`upload_to_gdrive.py`)
- Continuous monitoring with configurable intervals (`main.py`)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Activity Watch is running
- Kibana is running
- Elasticsearch is running
- Logstash is running
- winlogbeat is running
- Wireshark is installed with tshark in PATH
- Google Drive account
- Administrator privileges (required for packet capture)

### Google Drive Setup
1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.developers.google.com/)
   - Create a new project (or select existing one)
   - Enable the Google Drive API for your project

2. **Create OAuth 2.0 Credentials:**
   - In Google Cloud Console, go to "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application" as the application type
   - Download the JSON file and rename it to `credentials.json`
   - Place `credentials.json` in your project directory

3. **First-time Authentication:**
   - When you first run the script, a browser window will open
   - Log in to your Google account and authorize the application
   - The script will create a `token.pickle` file for future authentication

### Installation
1. Clone this repository or download the source code.
2. Install the required Python packages:
   ```powershell
   pip install -r requirements.txt
   ```
3. Copy your `credentials.json` file to the project directory
4. Configure your `.env` file with appropriate settings

### Usage
**Important:** Run PowerShell as Administrator for packet capture functionality.

Start the monitoring system:
```powershell
python main.py
```

The system will:
- Create a "Mitre-Dataset-Monitoring" folder in your Google Drive
- Create timestamped subfolders for each monitoring interval
- Upload all collected data directly to Google Drive
- Display an always-on-top clock during monitoring

### Data Structure in Google Drive
```
Google Drive/
└── Mitre-Dataset-Monitoring/
    ├── 20250912_105900/
    │   ├── screen_record_20250912_105900.avi
    │   ├── packet_capture_20250912_105900.pcap
    │   ├── syslogs_20250912_105900.json
    │   └── aw-watcher-web-chrome_logs_20250912_105900.json
    └── 20250912_111900/
        ├── screen_record_20250912_111900.avi
        ├── packet_capture_20250912_111900.pcap
        ├── syslogs_20250912_111900.json
        └── aw-watcher-web-chrome_logs_20250912_111900.json
```

### Configuration
Edit the `.env` file to customize:
- Monitoring intervals
- Screen recording settings
- Elasticsearch connection details
- File naming patterns

### Troubleshooting
- **Packet Capture Fails:** Ensure you're running as Administrator
- **Google Drive Authentication:** Delete `token.pickle` and re-authenticate
- **Missing Data:** Check that all prerequisite services are running
- **Upload Errors:** Verify your Google Cloud credentials and API quotas

## License
This project is licensed under the MIT License.
