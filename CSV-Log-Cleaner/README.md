# CSV Log Cleaner

Process logs from the CSV-Logs folder format into cleaned and merged JSON files.

## Input Format

- **System Logs**: CSV format (from Kibana export)
- **Browser Logs**: JSON format (ActivityWatch)
- **Network Logs**: PCAPNG or PCAP format (Wireshark/tcpdump)

## Output Format

Cleaned logs in the same format as `Annotate-attack-logs/Pseudo-Annotated-Logs`:

- Folder structure: `YYYYMMDD_HHMMSS/`
- File name: `annotated_data_YYYYMMDD_HHMMSS.json`
- Merged and sorted by timestamp

## Usage

```bash
python main.py
```

The script will:

1. Scan all folders in `E:\Hacking\Mitre-Dataset\CSV-Logs`
2. Extract timestamp from CSV log content
3. Parse all three log types
4. Merge and sort by timestamp
5. Output to `E:\Hacking\Mitre-Dataset\CSV-Logs-Cleaned`

## Requirements

```bash
pip install scapy
```

## Features

- **Timestamp Extraction**: Reads timestamp from CSV log content (format: "Jul 9, 2025 @ 20:25:45.081")
- **CSV Parsing**: Handles Kibana CSV export with `winlog.event_data.*` fields
- **PCAPNG Support**: Processes both .pcapng and .pcap network captures
- **Anonymization**: Generates consistent host_id and agent_id hashes
- **Timezone Handling**: Converts all timestamps to UTC ISO format
- **Error Handling**: Continues processing if individual log parsing fails

## Log Structure

Output JSON structure:

```json
{
  "session_id": "20250709_202545",
  "host_id": "4c84584a",
  "overall_label": "unlabeled",
  "logs": [
    {
      "timestamp": "2025-07-09T20:25:45.081Z",
      "event_type": "system|network|browser",
      "host_id": "4c84584a",
      "agent_id": "816d9d59",
      ...
    }
  ]
}
```
