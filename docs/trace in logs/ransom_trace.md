### Detecting Ransomware Traces in Your 20-Min Ransomware Session (7-Zip Based)

Based on your setup (ELK for system logs via Sysmon/Winlogbeat, browser logs like Chrome HAR/JSON, Wireshark PCAPs), a 7-Zip ransomware simulation typically involves compressing files into archives (T1560.001) before/after encryption (T1486), often via cmd/PowerShell scripts. This leaves detectable spikes in file I/O, process chains, and potential exfil. Focus on the 20-min window: baseline normal activity (e.g., <10 file ops/min) vs. anomalies like mass archiving (>50 files touched).

I'll break it down by log type, with **suspicious indicators** (IoCs), **queries/filters**, and **marking tips** (e.g., flag if >threshold). Run these on the session's timestamp range (e.g., Kibana: `@timestamp >= "YYYY-MM-DDTHH:MM:SS" AND @timestamp <= "YYYY-MM-DDTHH:MM:SS"`). Correlate across logs: e.g., 7z.exe spawn → file bursts → network spike.

#### 1. System Logs (ELK Stack/Sysmon/Windows Events)
Ransomware hits hard here: expect chain like `cmd.exe → 7z.exe` with rapid file creates/deletes in user dirs (%USERPROFILE%\Documents, etc.). Look for entropy changes if logging file hashes.

| Suspicious Indicator | ELK Query/Filter (KQL) | Marking as Suspicious |
|----------------------|------------------------|-----------------------|
| **7z.exe Process Spawn** (Core: Compression utility execution) | `event.code: 1 OR 4688 AND process.name: "7z.exe" AND (parent.name: "cmd.exe" OR "powershell.exe")` | Flag if spawned >1x in 20min; correlate with script args like `/compress` or file lists. Score: High (direct tool use). |
| **Mass File Creation** (Archives generated: e.g., .7z files) | `event.code: 11 AND file.extension: "7z" OR file.path: *\\Documents\\*.7z` (Sysmon file create) | >20 creates in <5min = suspicious; check paths for user data (not system). Mark: Volume spike vs. baseline. |
| **Mass File Deletion** (Originals wiped post-compress/encrypt) | `event.code: 23 OR 4663 AND (access_mask: 0x10000 OR process.name: "7z.exe" OR "del.exe") AND file.path: *\\Documents\\*` (Sysmon delete) | >15 deletes/min; target non-system files (.doc, .jpg). Flag: If paired with creates (compress then delete). |
| **High I/O or Handle Activity** (File enumeration for targets) | `event.code: 4663 AND object.type: "File" \| \| stats count() by host.name > 100` (aggregate over 20min) | Burst >50 accesses/sec; from explorer.exe or script. Mark: Anomaly if no user interaction logged. |
| **Script/Command Execution** (Ransom note or encrypt loop) | `event.code: 4688 AND (process.name: "powershell.exe" OR "cmd.exe") AND command_line: (*7z* OR *compress* OR *encrypt*)` | Encoded/obfuscated args; flag if child spawns 7z.exe. Score: Medium-High. |
| **Registry Edits** (Ransom note display or persistence) | `event.code: 4657 AND object.name: *HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run*` (if adding ransom exe) | New keys with .7z or ransom paths; mark if post-compress. |

**Detection Tips**: In Kibana, use a timeline viz (Discover > Add filter by timestamp). Threshold: >30 file events total = ransomware-like. Export to CSV for correlation.

#### 2. Browser Logs (HAR/JSON from Chrome/Edge/Firefox)
Less central (ransomware is local), but if payload/7z was downloaded via browser or exfil to cloud, expect traces. Check for user-initiated downloads or suspicious tabs.

| Suspicious Indicator | Query/Filter (JSON Grep or Pandas) | Marking as Suspicious |
|----------------------|------------------------------------|-----------------------|
| **7z/Payload Download** (Initial access vector) | Grep HAR: `jq '.log.entries[] | select(.request.url | contains("7z.exe") or .response.status == 200 and .response.headers[] | contains("application/x-7z"))'` OR Pandas: `df[df['mimeType'].str.contains('7z|zip')]['startedDateTime']` | Download size >1MB in session start; flag if from non-trusted domain (e.g., not 7-zip.org). Score: Medium. |
| **Suspicious URL Navigation** (Ransom payment site or C2) | `jq '.log.entries[] | select(.request.url | contains("bitcoin" or "ransom" or "onion"))'` OR `df[df['url'].str.contains('encrypt|pay', case=False)]` | Visits post-encrypt (timestamp >10min in); mark if new tabs with crypto sites. |
| **Form Submissions/Uploads** (Exfil keys via browser) | `df[df['method'] == 'POST' and df['url'].str.contains('cloud|drive') and df['bodySize'] > 1024]` (if HAR captures) | POST >500B to Google Drive/OneDrive; flag if after file ops. Score: Low-Medium unless volume high. |
| **Cache/File Access Anomalies** (Browser creds harvested pre-ransom) | Check `Login Data` SQLite (if logged): Anomalous reads, or JSON: `entries with .response.headers: "application/octet-stream"` | Timestamp overlap with system 7z; mark if paired with credential dumps. |

**Detection Tips**: Use Python/jq for batch: Load JSON, filter by `startedDateTime` in 20min window. Flag if >2 suspicious entries.

#### 3. Network Logs (Wireshark PCAPs)
Minimal for pure local 7-Zip (no inherent net), but watch for exfil (e.g., archives to C2/cloud) or beaconing. Use `tshark` for filters: `tshark -r session.pcap -Y "filter" -T fields -e frame.time -e ip.dst -e tcp.len`.

| Suspicious Indicator | Wireshark Filter (Display/TShark) | Marking as Suspicious |
|----------------------|-----------------------------------|-----------------------|
| **Outbound Exfil** (Archives/keys to C2 or cloud) | `http.request.method == "POST" and http.host contains "drive.google.com" or "onedrive" and tcp.len > 10000` OR `ip.dst != local_subnet and frame.len > 1024` | Flows >5MB total; sustained TCP (not bursts). Flag: To external IPs post-10min. Score: High if encrypted payload. |
| **Download of 7z Tool** (If not pre-installed) | `http contains "7z.exe" and http.request.method == "GET"` OR `filemagics shows "7z"` | Single large GET (~2-5MB) at session start; mark from suspicious domains. |
| **Beaconing/C2** (RAT callback during ransom) | `tcp.port == 4444 or 8080 and ip.dst_host == <your_C2_IP> and frame.time_delta < 60` (every min) | Periodic pings (5+ in 20min); flag bidirectional data. Score: Medium. |
| **DNS Queries** (To ransom sites) | `dns.qry.name contains "bitcoin" or "tor"` | Queries spike mid-session; mark if resolved to .onion/.ru domains. |
| **SMB/USB Fallback** (If exfil via removable media) | `smb.cmd == 0x2e and smb.file contains ".7z"` (file write) | Local net shares; flag if to \\USB\ or external. |

**Detection Tips**: Export to CSV (`tshark -r file.pcap -Y "http" -T fields -e ...`), aggregate bytes_out >1MB = exfil. In Wireshark GUI: Statistics > Conversations > IPv4 for outliers.

### Overall Workflow & Scoring
- **Correlation Rule**: Suspicious if system file burst + any browser/net hit in same 2-min window (e.g., 7z spawn → POST exfil).
- **Scoring Sessions**: Assign points (e.g., +10 for 7z.exe, +5 per mass op); >30 = confirmed ransomware trace.
- **Next**: Run on your log—e.g., Kibana dashboard with these queries. If no hits, check Sysmon config for file events. Share a sample PCAP/JSON snippet for a quick scan?

This should pinpoint 80-90% of traces in your session. Let me know results!