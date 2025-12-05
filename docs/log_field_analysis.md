# Log Field Analysis for MITRE ATT&CK Research
**Analysis Date:** December 5, 2025  
**Purpose:** Identify redundant and unnecessary fields for fine-tuning ML models to detect suspicious activity

---

## Executive Summary

This analysis examines three types of logs collected for MITRE ATT&CK research:
1. **System Logs** (Sysmon via Winlogbeat/Elasticsearch)
2. **Network Logs** (PCAP via Scapy)
3. **Browser Logs** (ActivityWatch)

Each log type contains numerous fields, many of which are redundant, metadata-heavy, or irrelevant for threat detection. This document categorizes fields by their importance for ML model training.

---

## 1. System Logs Analysis (Sysmon via ELK Stack)

### 1.1 Sample Structure
```json
{
  "timestamp": "2025-10-22T06:30:00.872Z",
  "event_type": "system",
  "message": "Network connection detected...",
  "winlog": {...},
  "@version": "1",
  "host": {...},
  "agent": {...},
  "tags": [...],
  "event": {...},
  "log": {...},
  "ecs": {...}
}
```

### 1.2 Field Classification

#### 🟢 **CRITICAL FIELDS** (Essential for Attack Detection)
| Field | Reason | MITRE Relevance |
|-------|--------|-----------------|
| `timestamp` | Temporal analysis, sequencing events | All techniques |
| `winlog.event_id` | Primary indicator of event type (1=Process, 3=Network, 11=FileCreate) | T1055, T1071, T1547 |
| `winlog.event_data.Image` | Process/executable path (detects malware execution) | T1059, T1106, T1204 |
| `winlog.event_data.ProcessId` | Correlation between events | T1055, T1036 |
| `winlog.event_data.ProcessGuid` | Unique process tracking across events | T1055, T1036 |
| `winlog.event_data.User` | Account involved in activity | T1078, T1136 |
| `winlog.event_data.SourceIp` | Network source (C2 detection) | T1071, T1090, T1571 |
| `winlog.event_data.DestinationIp` | Network destination (C2 detection) | T1071, T1090, T1571 |
| `winlog.event_data.DestinationPort` | Service identification (443, 4444, 8080) | T1071, T1571 |
| `winlog.event_data.Protocol` | Network protocol (tcp/udp) | T1071, T1095 |
| `winlog.event_data.TargetFilename` | File creation/modification paths | T1105, T1547, T1486 |
| `winlog.event_data.CommandLine` | Full command executed (detects PowerShell attacks) | T1059, T1087, T1003 |
| `winlog.event_data.ParentImage` | Parent process (detects suspicious spawning) | T1059, T1566 |
| `winlog.event_data.TargetObject` | Registry keys modified (persistence) | T1547, T1112 |

#### 🟡 **USEFUL BUT REDUNDANT FIELDS** (Can be derived or simplified)
| Field | Issue | Recommendation |
|-------|-------|----------------|
| `message` | Duplicates `winlog.event_data` in string format | **REMOVE** - Use structured `event_data` instead |
| `event.original` | Another duplicate of message | **REMOVE** - Redundant |
| `winlog.event_data.UtcTime` | Duplicates root `timestamp` | **REMOVE** - Use root timestamp |
| `winlog.computer_name` | Same as `host.name` | **REMOVE** - Use `host.name` |
| `winlog.event_data.SourceHostname` | Often same as `host.name` for outbound | **SIMPLIFY** - Only keep for inbound traffic |
| `winlog.event_data.DestinationHostname` | DNS name of destination | **OPTIONAL** - Keep only if analyzing domain-based attacks |
| `host.name` + `host_id` | Both identify the same machine | **KEEP ONE** - Use anonymized `host_id` only |
| `agent.name` + `agent_id` | Both identify the agent | **KEEP ONE** - Use anonymized `agent_id` only |

#### 🔴 **UNNECESSARY FIELDS** (Metadata/Infrastructure)
| Field | Reason to Remove |
|-------|------------------|
| `@version` | Logstash version - irrelevant for detection |
| `agent.ephemeral_id` | Temporary agent ID - changes frequently |
| `agent.type` | Always "winlogbeat" - no variance |
| `agent.version` | Version number - infrastructure metadata |
| `tags` | Logstash processing tags like `beats_input_codec_plain_applied` |
| `ecs.version` | ECS schema version - metadata |
| `log.level` | Usually "information" - low signal |
| `event.created` | When Elasticsearch received it - not when event occurred |
| `event.kind` | Always "event" - no variance |
| `event.provider` | Always "Microsoft-Windows-Sysmon" - redundant |
| `winlog.provider_guid` | GUID of provider - static value |
| `winlog.opcode` | Usually "Info" - low value |
| `winlog.version` | Event schema version - rarely useful |
| `winlog.record_id` | Sequential record number - not needed for ML |
| `winlog.channel` | Always "Microsoft-Windows-Sysmon/Operational" |
| `winlog.task` | Verbose event description (duplicates event_id) |
| `winlog.user.identifier` | Windows SID like "S-1-5-18" - use User field instead |
| `winlog.user.type` | Always "User" |
| `winlog.user.domain` | Often "NT AUTHORITY" for system events |
| `winlog.process.thread.id` | Thread ID - too granular for ML |
| `winlog.process.pid` | Winlogbeat process, not the logged process |
| `winlog.event_data.SourceIsIpv6` | Binary flag - merge with IP field |
| `winlog.event_data.DestinationIsIpv6` | Binary flag - merge with IP field |
| `winlog.event_data.SourcePortName` | Usually "-" (empty) |
| `winlog.event_data.DestinationPortName` | Often "https" but redundant with port number |
| `winlog.event_data.Initiated` | Usually "true" for outbound - low signal |

### 1.3 Fields to KEEP in System Logs (Preserve Exact Structure)
```json
{
  "timestamp": "2025-10-22T06:30:00.872Z",
  "event_type": "system",
  "winlog": {
    "event_id": "3",
    "event_data": {
      "Image": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
      "ProcessId": "11052",
      "ProcessGuid": "{ABFC3109-5B72-68F8-8F02-000000002E00}",
      "ParentImage": "C:\\Windows\\explorer.exe",
      "CommandLine": "chrome.exe --type=renderer",
      "User": "DESKTOP-7TQ88T1\\Niloy",
      "SourceIp": "10.43.0.105",
      "SourcePort": "50487",
      "DestinationIp": "216.58.200.170",
      "DestinationPort": "443",
      "Protocol": "udp",
      "TargetFilename": "C:\\Users\\Niloy\\Downloads\\Crypted.exe",
      "TargetObject": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    }
  },
  "host_id": "4c84584a",
  "agent_id": "816d9d59"
}
```

### 1.4 Fields to REMOVE from System Logs
```json
{
  "message": "...",  // ❌ Remove - duplicates event_data
  "@version": "1",  // ❌ Remove - Logstash metadata
  "winlog": {
    "opcode": "Info",  // ❌ Remove
    "computer_name": "DESKTOP-7TQ88T1",  // ❌ Remove - use host_id
    "channel": "Microsoft-Windows-Sysmon/Operational",  // ❌ Remove
    "task": "Network connection detected...",  // ❌ Remove
    "record_id": 317430,  // ❌ Remove
    "version": 5,  // ❌ Remove
    "provider_name": "Microsoft-Windows-Sysmon",  // ❌ Remove
    "provider_guid": "{5770385F-C22A-43E0-BF4C-06F5698FFBD9}",  // ❌ Remove
    "user": {  // ❌ Remove entire section
      "name": "SYSTEM",
      "identifier": "S-1-5-18",
      "type": "User",
      "domain": "NT AUTHORITY"
    },
    "process": {  // ❌ Remove entire section
      "thread": {"id": 2840},
      "pid": 4060
    },
    "event_data": {
      "UtcTime": "2025-10-20 00:44:28.897",  // ❌ Remove - duplicates timestamp
      "SourceHostname": "DESKTOP-7TQ88T1",  // ❌ Remove - usually same as host
      "DestinationHostname": "del11s06-in-f10.1e100.net",  // ❌ Remove - optional
      "SourceIsIpv6": "false",  // ❌ Remove
      "DestinationIsIpv6": "false",  // ❌ Remove
      "SourcePortName": "-",  // ❌ Remove
      "DestinationPortName": "https",  // ❌ Remove - redundant with port number
      "Initiated": "true",  // ❌ Remove
      "RuleName": "Common Ports"  // ❌ Remove
    }
  },
  "host": {  // ❌ Remove entire section - use host_id instead
    "name": "DESKTOP-7TQ88T1"
  },
  "agent": {  // ❌ Remove entire section - use agent_id instead
    "ephemeral_id": "85dbddee-7f40-4532-b9de-0c4dc9ec7eb2",
    "id": "ed729226-ba3a-4d44-a977-17ed06c8d3ca",
    "name": "DESKTOP-7TQ88T1",
    "type": "winlogbeat",
    "version": "9.0.2"
  },
  "tags": ["beats_input_codec_plain_applied"],  // ❌ Remove
  "event": {  // ❌ Remove entire section
    "original": "...",
    "created": "2025-10-22T06:30:01.980Z",
    "kind": "event",
    "provider": "Microsoft-Windows-Sysmon",
    "action": "Network connection detected...",
    "code": "3"
  },
  "log": {  // ❌ Remove entire section
    "level": "information"
  },
  "ecs": {  // ❌ Remove entire section
    "version": "8.0.0"
  }
}
```

**Space Reduction:** ~70% reduction by removing redundant fields

---

## 2. Network Logs Analysis (PCAP via Scapy)

### 2.1 Sample Structure
```json
{
  "timestamp": "2025-10-22T06:30:34.409Z",
  "event_type": "network",
  "packet_number": 1,
  "length": 60,
  "summary": "Ether / IP / TCP 52.123.129.14:https > 10.43.0.105:61416 RA / Padding",
  "raw_hex": "f48e38804aef6c3b6bc755df0800450000289b5f...",
  "layers": {
    "Ether": {...},
    "IP": {...},
    "TCP": {...},
    "Padding": {...}
  }
}
```

### 2.2 Field Classification

#### 🟢 **CRITICAL FIELDS** (Essential for Attack Detection)
| Field | Reason | MITRE Relevance |
|-------|--------|-----------------|
| `timestamp` | Temporal analysis, traffic patterns | All network techniques |
| `length` | Packet size (detects exfiltration, beaconing) | T1041, T1071, T1030 |
| `layers.IP.src` | Source IP address | T1071, T1090, T1571 |
| `layers.IP.dst` | Destination IP address | T1071, T1090, T1571 |
| `layers.TCP.sport` or `layers.UDP.sport` | Source port | T1571, T1090 |
| `layers.TCP.dport` or `layers.UDP.dport` | Destination port (C2 detection) | T1571, T1071 |
| `layers.TCP.flags` | TCP flags (SYN, ACK, RST) - detects scanning | T1046, T1571 |
| `layers.IP.proto` | Protocol number (6=TCP, 17=UDP) | T1095, T1571 |
| `layers.TCP.seq` | Sequence number (for session reconstruction) | T1071, T1571 |
| `layers.TCP.ack` | Acknowledgment number | T1071 |

#### 🟡 **USEFUL BUT REDUNDANT FIELDS**
| Field | Issue | Recommendation |
|-------|-------|----------------|
| `summary` | Human-readable duplicate of layer data | **REMOVE** - Reconstruct from layers if needed |
| `layers.IP.len` | Duplicates root `length` field | **REMOVE** - Use root `length` |
| `layers.IP.ttl` | Time-to-live (useful for OS fingerprinting but not critical) | **OPTIONAL** - Keep for advanced analysis |
| `layers.Ether.dst` | MAC address of destination | **REMOVE** - Not useful for network-level analysis |
| `layers.Ether.src` | MAC address of source | **REMOVE** - Local network only |
| `layers.Ether.type` | Usually 2048 (IPv4) | **REMOVE** - Redundant with IP layer |

#### 🔴 **UNNECESSARY FIELDS** (Low Value for ML)
| Field | Reason to Remove |
|-------|------------------|
| `packet_number` | Sequential numbering - position in PCAP, not temporal |
| `raw_hex` | Full packet bytes in hex - too large, not ML-friendly |
| `layers.IP.version` | Always "4" (IPv4) - no variance |
| `layers.IP.ihl` | IP header length - infrastructure detail |
| `layers.IP.tos` | Type of service - rarely used |
| `layers.IP.id` | IP identification - fragmentation tracking |
| `layers.IP.flags` | IP flags (DF) - rarely relevant |
| `layers.IP.frag` | Fragment offset - usually 0 |
| `layers.IP.chksum` | IP checksum - error detection only |
| `layers.IP.options` | Usually empty list `[]` |
| `layers.TCP.dataofs` | TCP data offset - header size |
| `layers.TCP.reserved` | Reserved bits - always 0 |
| `layers.TCP.window` | Window size - TCP flow control, not attack indicator |
| `layers.TCP.chksum` | TCP checksum - error detection |
| `layers.TCP.urgptr` | Urgent pointer - rarely used |
| `layers.TCP.options` | Usually empty `[]` |
| `layers.Padding.load` | Padding bytes to meet minimum frame size |

### 2.3 Fields to KEEP in Network Logs (Preserve Exact Structure)
```json
{
  "timestamp": "2025-10-22T06:30:34.409Z",
  "event_type": "network",
  "length": 60,
  "layers": {
    "IP": {
      "src": "52.123.129.14",
      "dst": "10.43.0.105",
      "proto": "6",
      "ttl": "110"
    },
    "TCP": {
      "sport": "443",
      "dport": "61416",
      "flags": "RA",
      "seq": "1585356840",
      "ack": "257718799"
    },
    "UDP": {  // If UDP packet
      "sport": "53",
      "dport": "12345"
    }
  }
}
```

### 2.4 Fields to REMOVE from Network Logs
```json
{
  "packet_number": 1,  // ❌ Remove - sequential numbering
  "summary": "Ether / IP / TCP 52.123.129.14:https > 10.43.0.105:61416 RA / Padding",  // ❌ Remove - duplicates layer data
  "raw_hex": "f48e38804aef6c3b6bc755df0800450000289b5f...",  // ❌ Remove - too large
  "layers": {
    "Ether": {  // ❌ Remove entire Ethernet layer
      "dst": "f4:8e:38:80:4a:ef",
      "src": "6c:3b:6b:c7:55:df",
      "type": "2048"
    },
    "IP": {
      "version": "4",  // ❌ Remove - always 4
      "ihl": "5",  // ❌ Remove
      "tos": "0",  // ❌ Remove
      "len": "40",  // ❌ Remove - duplicates root 'length'
      "id": "39775",  // ❌ Remove
      "flags": "DF",  // ❌ Remove
      "frag": "0",  // ❌ Remove
      "chksum": "45395",  // ❌ Remove
      "options": "[]"  // ❌ Remove
    },
    "TCP": {
      "dataofs": "5",  // ❌ Remove
      "reserved": "0",  // ❌ Remove
      "window": "0",  // ❌ Remove
      "chksum": "30205",  // ❌ Remove
      "urgptr": "0",  // ❌ Remove
      "options": "[]"  // ❌ Remove
    },
    "Padding": {  // ❌ Remove entire Padding layer
      "load": "b'\\x00\\x00\\x00\\x00\\x00\\x00'"
    }
  }
}
```

**Space Reduction:** ~80% reduction by removing unnecessary protocol details

**Critical Detection Patterns:**
- **C2 Beaconing:** Small packets (54-60 bytes) with ACK flags at regular intervals
- **Data Exfiltration:** Large packets (>500 bytes) to external IPs
- **Port Scanning:** Multiple SYN packets to different ports

---

## 3. Browser Logs Analysis (ActivityWatch)

### 3.1 Sample Structure
```json
{
  "timestamp": "2025-10-22T06:34:18.747Z",
  "event_type": "browser",
  "id": 7453,
  "duration": 5.093,
  "data": {
    "url": "https://chatgpt.com/c/68f86135-88f4-8322-8146-9bf5cd8feefb",
    "title": "Running activity watch as service",
    "audible": false,
    "incognito": false,
    "tabCount": 7
  }
}
```

### 3.2 Field Classification

#### 🟢 **CRITICAL FIELDS** (Essential for Attack Detection)
| Field | Reason | MITRE Relevance |
|-------|--------|-----------------|
| `timestamp` | When URL was accessed | T1566, T1071 |
| `data.url` | Full URL (detects phishing, C2 domains, download sites) | T1566, T1071, T1608 |
| `data.title` | Page title (contextual clues) | T1566, T1608 |
| `duration` | Time spent on page (quick visits = suspicious) | T1566, T1204 |

#### 🟡 **USEFUL BUT OPTIONAL FIELDS**
| Field | Value | Recommendation |
|-------|-------|----------------|
| `data.incognito` | Whether incognito mode used | **KEEP** - Indicates user trying to hide activity |
| `data.tabCount` | Number of open tabs | **OPTIONAL** - Weak signal |

#### 🔴 **UNNECESSARY FIELDS**
| Field | Reason to Remove |
|-------|------------------|
| `id` | ActivityWatch internal event ID - sequential numbering |
| `data.audible` | Whether page made sound - irrelevant for security |

### 3.3 Fields to KEEP in Browser Logs (Preserve Exact Structure)
```json
{
  "timestamp": "2025-10-22T06:34:18.747Z",
  "event_type": "browser",
  "duration": 5.093,
  "data": {
    "url": "https://chatgpt.com/c/68f86135-88f4-8322-8146-9bf5cd8feefb",
    "title": "Running activity watch as service",
    "incognito": false
  }
}
```

### 3.4 Fields to REMOVE from Browser Logs
```json
{
  "id": 7453,  // ❌ Remove - ActivityWatch internal ID
  "data": {
    "audible": false,  // ❌ Remove - not security relevant
    "tabCount": 7  // ❌ Remove - weak signal (optional)
  }
}
```

**Space Reduction:** ~40% reduction

**Critical Detection Patterns:**
- **Phishing Sites:** Short visits (<5 sec) to credential harvesting sites
- **Download Activity:** URLs ending in `.exe`, `.zip`, `.rar`
- **C2 Domains:** Visits to suspicious/non-standard domains
- **File Sharing:** Dropbox, Google Drive, Mega during exfiltration

---

## 4. Cross-Log Redundancy Issues

### 4.1 Timestamp Inconsistencies
- **System Logs:** `@timestamp` (Elasticsearch), `winlog.event_data.UtcTime` (Sysmon)
- **Network Logs:** `pkt.time` (Unix timestamp in float)
- **Browser Logs:** `timestamp` (ISO format with timezone)

**Solution:** Standardize all to ISO 8601 UTC format: `YYYY-MM-DDTHH:mm:ss.sssZ`

### 4.2 IP Address Duplication
Network events appear in both:
- **System Logs:** `winlog.event_data.SourceIp` / `DestinationIp` (Sysmon Event ID 3)
- **Network Logs:** `layers.IP.src` / `dst` (PCAP)

**Solution:** Use network logs as ground truth for all packet-level analysis

### 4.3 Host Identification
Multiple identifiers for same machine:
- `host.name`: "DESKTOP-7TQ88T1"
- `host_id`: "4c84584a" (anonymized hash)
- `agent.name`: "DESKTOP-7TQ88T1"
- `agent.id`: "ed729226-ba3a-4d44-a977-17ed06c8d3ca"
- `winlog.computer_name`: "DESKTOP-7TQ88T1"

**Solution:** Use single anonymized `host_id` throughout

---

## 5. Field Importance for ML Model Training

### 5.1 Feature Priority Matrix

| Priority | System Log Fields | Network Log Fields | Browser Log Fields |
|----------|-------------------|--------------------|--------------------|
| **P0** (Critical) | event_id, Image, ProcessId, CommandLine, DestinationIp, DestinationPort | src_ip, dst_ip, dst_port, packet_size, tcp_flags | url, domain, duration |
| **P1** (High) | User, ParentImage, Protocol, SourceIp | src_port, protocol, seq_num, ttl | title, incognito |
| **P2** (Medium) | ProcessGuid, TargetFilename, TargetObject | ack_num | tabCount |
| **P3** (Low) | All other structured fields | - | - |
| **REMOVE** | message, event.original, metadata fields | raw_hex, checksums, MAC addresses | id, audible |

### 5.2 Estimated Storage Reduction

| Log Type | Original Size | Minimal Size | Reduction |
|----------|--------------|--------------|-----------|
| System Log (per event) | ~2.5 KB | ~0.8 KB | **68%** |
| Network Log (per packet) | ~1.2 KB | ~0.25 KB | **79%** |
| Browser Log (per event) | ~0.4 KB | ~0.25 KB | **38%** |
| **Total Dataset** | **100 GB** | **~35 GB** | **~65%** |

---

## 6. Recommended Unified Schema for ML Training

### 6.1 Normalized Event Structure
All events share this base structure:

```json
{
  "timestamp": "2025-10-22T06:30:00.872Z",
  "event_type": "system|network|browser",
  "host_id": "4c84584a",
  "label": "suspicious|benign",
  "mitre_techniques": ["T1071", "T1090"],
  "confidence_score": 0.85,
  
  // Event-specific fields follow
  "system": {...},  // Only present for system events
  "network": {...}, // Only present for network events
  "browser": {...}  // Only present for browser events
}
```

### 6.2 Feature Engineering Recommendations

#### Derived Features (Add These)
1. **Time-based:**
   - `hour_of_day` (0-23)
   - `day_of_week` (0-6)
   - `is_business_hours` (boolean)

2. **Process-based (System Logs):**
   - `is_suspicious_parent` (Word/Excel spawning cmd.exe/powershell.exe)
   - `process_depth` (number of parent processes)
   - `common_process_path` (boolean - is it in System32/Program Files)

3. **Network-based:**
   - `is_external_ip` (boolean)
   - `is_common_port` (boolean - 80, 443, 53, 22)
   - `packets_per_second` (aggregated metric)
   - `avg_packet_size` (aggregated metric)

4. **Browser-based:**
   - `is_download_url` (boolean - contains .exe, .zip, etc.)
   - `domain_reputation` (from threat intel)
   - `visit_count` (frequency of domain visits)

---

## 7. Attack Detection Use Cases

### 7.1 C2 Communication Detection
**Relevant Fields:**
- System: `event_id=3`, `DestinationIp`, `DestinationPort`, `Image`
- Network: `dst_ip`, `dst_port`, `packet_size`, `tcp_flags`

**Patterns:**
- Small packets (54-60 bytes) with ACK-only flags
- Regular intervals (beaconing)
- Non-standard ports (4444, 8080, 1337, 5000)
- Unknown foreign IPs

### 7.2 Data Exfiltration Detection
**Relevant Fields:**
- Network: `src_ip` (internal), `dst_ip` (external), `packet_size` (>500 bytes)
- Browser: `url` (contains dropbox.com, drive.google.com, mega.nz)
- System: `event_id=11` (file creation in staging area)

**Patterns:**
- Large outbound packets to cloud storage
- Browser visits to file sharing sites correlated with large uploads
- Files created in temp folders then deleted

### 7.3 Malware Execution Detection
**Relevant Fields:**
- System: `event_id=1`, `Image`, `ParentImage`, `CommandLine`
- Browser: `url` (download links), `title`

**Patterns:**
- Executables run from Downloads, Temp, or AppData
- Suspicious parent-child relationships (explorer.exe → malware.exe)
- PowerShell with encoded commands
- Browser downloads followed immediately by process creation

### 7.4 Persistence Mechanism Detection
**Relevant Fields:**
- System: `event_id=13` (registry), `TargetObject`, `Image`

**Patterns:**
- Registry modifications in `Run`, `RunOnce`, `Services` keys
- Scheduled task creation
- Startup folder modifications

### 7.5 Credential Harvesting Detection
**Relevant Fields:**
- System: `event_id=1`, `Image` (contains "WebBrowserPassView", credential dumping tools)
- Browser: `url` (phishing sites), `duration` (<5 sec)

**Patterns:**
- Known credential stealing tools executed
- Browser visits to credential harvesting forms
- Quick page visits (user entering credentials and leaving)

---

## 8. Implementation Recommendations

### 8.1 Data Preprocessing Pipeline
```python
# Filter logs to remove unnecessary fields while keeping original structure
def preprocess_log_entry(raw_log):
    # Standardize timestamp
    raw_log['timestamp'] = standardize_timestamp(raw_log['timestamp'])
    
    # Anonymize host/agent identifiers (add if not present)
    if 'host' in raw_log and 'host_id' not in raw_log:
        raw_log['host_id'] = anonymize(raw_log['host']['name'])
    if 'agent' in raw_log and 'agent_id' not in raw_log:
        raw_log['agent_id'] = anonymize(raw_log['agent']['id'])
    
    # Filter fields based on log type
    if raw_log['event_type'] == 'system':
        filtered_log = filter_system_fields(raw_log)
    elif raw_log['event_type'] == 'network':
        filtered_log = filter_network_fields(raw_log)
    elif raw_log['event_type'] == 'browser':
        filtered_log = filter_browser_fields(raw_log)
    else:
        filtered_log = raw_log
    
    return filtered_log
```

### 8.2 Field Filtering Functions (Keep Original Structure)
```python
def filter_system_fields(log):
    """Keep only essential fields, preserve original structure"""
    filtered = {
        'timestamp': log['timestamp'],
        'event_type': log['event_type'],
        'winlog': {
            'event_id': log['winlog']['event_id'],
            'event_data': {}
        }
    }
    
    # Keep only essential event_data fields
    essential_fields = [
        'Image', 'ProcessId', 'ProcessGuid', 'User', 'CommandLine',
        'ParentImage', 'SourceIp', 'SourcePort', 'DestinationIp',
        'DestinationPort', 'Protocol', 'TargetFilename', 'TargetObject'
    ]
    
    for field in essential_fields:
        if field in log['winlog']['event_data']:
            filtered['winlog']['event_data'][field] = log['winlog']['event_data'][field]
    
    # Keep anonymized host/agent IDs
    if 'host_id' in log:
        filtered['host_id'] = log['host_id']
    if 'agent_id' in log:
        filtered['agent_id'] = log['agent_id']
    
    return filtered

def filter_network_fields(log):
    """Keep only essential fields, preserve original structure"""
    filtered = {
        'timestamp': log['timestamp'],
        'event_type': log['event_type'],
        'length': log['length'],
        'layers': {}
    }
    
    # Keep essential IP layer fields
    if 'IP' in log['layers']:
        filtered['layers']['IP'] = {
            'src': log['layers']['IP']['src'],
            'dst': log['layers']['IP']['dst'],
            'proto': log['layers']['IP']['proto'],
            'ttl': log['layers']['IP'].get('ttl')
        }
    
    # Keep essential TCP layer fields
    if 'TCP' in log['layers']:
        filtered['layers']['TCP'] = {
            'sport': log['layers']['TCP']['sport'],
            'dport': log['layers']['TCP']['dport'],
            'flags': log['layers']['TCP']['flags'],
            'seq': log['layers']['TCP']['seq'],
            'ack': log['layers']['TCP']['ack']
        }
    
    # Keep essential UDP layer fields
    if 'UDP' in log['layers']:
        filtered['layers']['UDP'] = {
            'sport': log['layers']['UDP']['sport'],
            'dport': log['layers']['UDP']['dport']
        }
    
    return filtered

def filter_browser_fields(log):
    """Keep only essential fields, preserve original structure"""
    filtered = {
        'timestamp': log['timestamp'],
        'event_type': log['event_type'],
        'duration': log['duration'],
        'data': {
            'url': log['data']['url'],
            'title': log['data']['title'],
            'incognito': log['data']['incognito']
        }
    }
    
    return filtered
```

### 8.3 Annotation Strategy
For labeling data as "suspicious" or "benign":

1. **Automated Rules** (high confidence):
   - Known C2 IPs from threat intel
   - Known malicious domains
   - Specific MITRE technique patterns

2. **Semi-Supervised** (medium confidence):
   - Statistical anomalies (rare processes, unusual ports)
   - Temporal patterns (late-night activity)
   - Correlation across log types

3. **Manual Review** (uncertain cases):
   - Ambiguous patterns
   - New attack variants
   - False positive reduction

---

## 9. Conclusion

### 9.1 Key Findings
1. **Redundancy is significant:** 60-80% of fields are duplicates, metadata, or low-value
2. **System logs are most bloated:** ELK stack adds extensive metadata
3. **Network logs have excessive detail:** Raw hex and checksums are unnecessary
4. **Browser logs are cleanest:** Already fairly minimal

### 9.2 Actionable Steps
1. ✅ **Implement minimal schema** as defined in sections 1.3, 2.3, 3.3
2. ✅ **Remove all fields** marked in red (🔴)
3. ✅ **Engineer derived features** from section 6.2
4. ✅ **Standardize timestamps** across all log types
5. ✅ **Anonymize identifiers** (host_id, agent_id)
6. ✅ **Add MITRE technique labels** based on detection patterns in section 7

### 9.3 Expected Outcomes
- **65% storage reduction** (100 GB → 35 GB)
- **Faster ML training** due to fewer features
- **Better model performance** by removing noise
- **Easier annotation** with focused, relevant fields
- **Improved interpretability** of model decisions

---

## 10. References

### MITRE ATT&CK Techniques Mentioned
- **T1003:** OS Credential Dumping
- **T1030:** Data Transfer Size Limits
- **T1041:** Exfiltration Over C2 Channel
- **T1046:** Network Service Scanning
- **T1055:** Process Injection
- **T1059:** Command and Scripting Interpreter
- **T1071:** Application Layer Protocol (C2)
- **T1078:** Valid Accounts
- **T1087:** Account Discovery
- **T1090:** Proxy
- **T1095:** Non-Application Layer Protocol
- **T1105:** Ingress Tool Transfer
- **T1106:** Native API
- **T1112:** Modify Registry
- **T1136:** Create Account
- **T1204:** User Execution
- **T1486:** Data Encrypted for Impact (Ransomware)
- **T1547:** Boot or Logon Autostart Execution
- **T1566:** Phishing
- **T1571:** Non-Standard Port
- **T1572:** Protocol Tunneling
- **T1608:** Stage Capabilities

### Sysmon Event IDs Reference
- **1:** Process Creation
- **3:** Network Connection
- **5:** Process Terminated
- **7:** Image Loaded (DLL)
- **11:** File Created
- **13:** Registry Value Set
- **22:** DNS Query

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Author:** Log Analysis for MITRE Research Project
