### Detecting Traces of Your File Edit/Delete Attack via Mega Payload

In your simulated attack—delivering a payload via Mega.nz link (cloud-based ingress, akin to T1105), user download/execution for initial access (T1204.002), and post-access file edits/deletes (T1070.004, T1565.001)—focus on the 20-min session window. Expect traces starting with browser/network for download, then system for execution/edits, and potential RAT callbacks.

Your logs (ELK for system via Sysmon/Winlogbeat, browser JSON/HAR, Wireshark PCAPs) should capture these. I'll outline by log type: **suspicious indicators** (IoCs like processes, files), **queries/filters**, and **marking tips** (e.g., thresholds for anomalies). Correlate timestamps: e.g., Mega download → payload exec → file ops within minutes.

#### 1. System Logs (ELK Stack/Sysmon/Windows Events)
Core traces: Payload execution chain (e.g., explorer.exe → payload.exe), then file handle ops for edits/deletes. Look for spikes in %TEMP%/Downloads and user dirs.

| Suspicious Indicator | ELK Query/Filter (KQL) | Marking as Suspicious |
|----------------------|------------------------|-----------------------|
| **Payload Execution** (User click on downloaded file) | `event.code: 4688 AND parent.name: "explorer.exe" AND (process.name: "*.exe" OR process.command_line: "*mega*" OR file.hash: <known_payload_hash>)` | Spawn in first 5min; flag if from Downloads/%TEMP%. Score: High (initial access). |
| **File Edits** (Manipulation via RAT) | `event.code: 4663 AND object.type: "File" AND (access_mask: 0x4 OR process.name: "cmd.exe" OR "powershell.exe") AND file.path: *\\Users\\*` (write access) | >10 writes/min to non-system files (.txt, .doc); mark if RAT process (e.g., Revenge RAT exe) is parent. |
| **File Deletes** (Cleanup or impact) | `event.code: 23 OR 4663 AND (access_mask: 0x10000 OR process.name: "del.exe" OR "rm.exe") AND file.path: *\\Users\\* OR *\\Temp\\*` (Sysmon delete) | Burst >15 deletes in <5min; flag targeted paths (e.g., Documents). Score: High if post-access. |
| **RAT Process/Activity** (Control after access) | `event.code: 1 OR 4688 AND (process.name: "*rat.exe*" OR command_line: "*connect*")` | Child processes from payload; mark persistent runs (e.g., registry adds). |
| **Registry Changes** (If RAT persists) | `event.code: 4657 AND object.name: *HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run*` | New entries post-download; flag paths to payload. |

**Detection Tips**: Use Kibana timeline for sequence (download event → ops). Threshold: >20 file events total = attack-like. If Sysmon is tuned for FileDelete, expect clear hits.

#### 2. Browser Logs (HAR/JSON from Chrome/Edge/Firefox)
Traces here center on Mega link access/download. Edits/deletes are local, but watch for any RAT-induced browser interactions (e.g., credential harvest).

| Suspicious Indicator | Query/Filter (JSON Grep or Pandas) | Marking as Suspicious |
|----------------------|------------------------------------|-----------------------|
| **Mega Link Navigation/Download** (Phishing link click) | Grep: `jq '.log.entries[] | select(.request.url | contains("mega.nz" or "mega.io")) and .response.status == 200'` OR Pandas: `df[df['url'].str.contains('mega.nz', case=False) & (df['mimeType'].str.contains('exe|zip') or df['bodySize'] > 100000)]` | GET/POST to mega.nz early in session; flag file downloads (>100KB). Score: High (delivery vector). |
| **Suspicious Referrers** (Link from email/messaging) | `jq '.log.entries[] | select(.request.headers[] | contains("referer: *messaging*"))'` OR `df[df['referer'].str.contains('mail|chat', case=False)]` | Referrer not from trusted sites; mark if leads to download. |
| **Post-Access Activity** (If RAT uses browser) | `df[(df['method'] == 'POST') & (df['startedDateTime'] > <access_time>) & df['url'].str.contains('c2|rat')]` | Anomalous requests after 5min; flag if to external domains. Score: Medium. |

**Detection Tips**: Filter by `startedDateTime` in 20min range. Use Python/jq to extract downloads; correlate with system exec timestamps.

#### 3. Network Logs (Wireshark PCAPs)
Expect outbound to Mega for download, then RAT C2 for access/control, and minimal for local edits/deletes unless exfil.

| Suspicious Indicator | Wireshark Filter (Display/TShark) | Marking as Suspicious |
|----------------------|-----------------------------------|-----------------------|
| **Mega Download Traffic** (Payload ingress) | `http.host contains "mega.nz" and http.request.method == "GET" and frame.len > 1024` OR `tcp.port == 443 and ip.dst_host == "mega.nz"` | Large HTTPS GET early; flag content-type "application/octet-stream". Score: High. |
| **RAT C2 Connection** (Access after click) | `tcp.port == 4444 or 8080 and ip.dst != local_subnet and frame.time_delta < 60` (beaconing) | Bidirectional post-download (5+ packets); mark sustained flows. |
| **DNS Queries** (To Mega or C2) | `dns.qry.name contains "mega.nz" or "your_c2_domain"` | Resolves in first 2min; flag non-standard domains. Score: Medium. |
| **Exfil/Control Data** (If edits sent back) | `http.request.method == "POST" and tcp.len > 500 and ip.dst != local` | POST bursts mid-session; mark if after file ops timestamps. |

**Detection Tips**: Use `tshark -r file.pcap -Y "http contains mega" -T fields -e frame.time -e http.request.uri` for CSV export. Aggregate outbound bytes >500KB = suspicious.

### Overall Analysis Workflow
- **Correlation**: Link browser Mega hit → system payload spawn → file edit/delete events (e.g., via shared timestamps).
- **Scoring**: +10 for download trace, +15 per file op burst; >30 = confirmed attack.
- **Enhancements**: If no hits, verify Sysmon rules for FileDelete/Modify. Run on your log exports for patterns.

This covers key traces—start with ELK for system ops, then cross-check network/browser. Share sample log snippets for targeted tweaks!