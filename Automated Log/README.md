# Automated Log Extraction and Monitoring

This project provides scripts for extracting system logs, browser logs, monitoring system activity, capturing network packets, and recording the screen. It is designed to help automate the collection and synchronization of various logs for analysis and troubleshooting.

## Features
- Extract system logs (`extract_syslogs.py`)
- Extract browser logs (`extract_browser_logs.py`)
- Monitor system activity (`monitoring_controller.py`)
- Capture network packets (`packet_capture.py`)
- Record screen activity (`screen_recorder.py`)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Activity Watch is running
- Kibana is running
- Elasticsearch is running
- Logstash is running
- winlogbeat is running
- wireshark is installed with the necessary plugins

### Installation
1. Clone this repository or download the source code.
2. Install the required Python packages:
   ```powershell
   pip install -r requirements.txt
   ```

### Usage
Just run the main script to start monitoring and extracting logs:
```powershell
python main.py
```

## License
This project is licensed under the MIT License.
