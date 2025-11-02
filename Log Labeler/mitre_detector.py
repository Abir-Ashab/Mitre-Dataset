"""MITRE ATT&CK detection using Gemini AI - Story-based approach."""
import os
import json
import time
from typing import Dict, List
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LOG_TYPE = os.getenv('LOG_TYPE', 'normal')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MITRE_REFERENCE = """
Common MITRE ATT&CK Techniques:

Initial Access:
- T1566: Phishing
  - T1566.001: Spearphishing Attachment
  - T1566.002: Spearphishing Link
  - T1566.003: Spearphishing via Service
- T1078: Valid Accounts
  - T1078.001: Default Accounts
  - T1078.002: Domain Accounts
  - T1078.003: Local Accounts
  - T1078.004: Cloud Accounts

Execution:
- T1059: Command and Scripting Interpreter
  - T1059.001: PowerShell
  - T1059.003: Windows Command Shell
  - T1059.005: Visual Basic
  - T1059.007: JavaScript
- T1204: User Execution
  - T1204.001: Malicious Link
  - T1204.002: Malicious File
- T1053: Scheduled Task/Job
  - T1053.002: At
  - T1053.005: Scheduled Task

Persistence:
- T1547: Boot or Logon Autostart Execution
  - T1547.001: Registry Run Keys
  - T1547.004: Winlogon Helper DLL
  - T1547.009: Shortcut Modification
- T1543: Create or Modify System Process
  - T1543.003: Windows Service
- T1546: Event Triggered Execution
  - T1546.003: Windows Management Instrumentation

Privilege Escalation:
- T1548: Abuse Elevation Control Mechanism
  - T1548.002: Bypass User Account Control
  - T1548.003: Sudo and Sudo Caching
  - T1548.004: Elevated Execution with Prompt
- T1134: Access Token Manipulation
  - T1134.001: Token Impersonation/Theft
  - T1134.002: Create Process with Token

Defense Evasion:
- T1562: Impair Defenses
  - T1562.001: Disable or Modify Tools
  - T1562.002: Disable Windows Event Logging
  - T1562.004: Disable or Modify System Firewall
- T1070: Indicator Removal
  - T1070.001: Clear Windows Event Logs
  - T1070.003: Clear Command History
  - T1070.004: File Deletion
  - T1070.006: Timestomp
- T1140: Deobfuscate/Decode Files or Information

Credential Access:
- T1003: OS Credential Dumping
  - T1003.001: LSASS Memory
  - T1003.002: Security Account Manager
  - T1003.003: NTDS
  - T1003.008: /etc/passwd and /etc/shadow
- T1555: Credentials from Password Stores
  - T1555.003: Credentials from Web Browsers
  - T1555.004: Windows Credential Manager
- T1110: Brute Force
  - T1110.001: Password Guessing
  - T1110.002: Password Cracking
  - T1110.003: Password Spraying
  - T1110.004: Credential Stuffing

Discovery:
- T1083: File and Directory Discovery
- T1082: System Information Discovery
- T1016: System Network Configuration Discovery
  - T1016.001: Internet Connection Discovery
- T1033: System Owner/User Discovery
- T1087: Account Discovery
  - T1087.001: Local Account
  - T1087.002: Domain Account
- T1046: Network Service Discovery
- T1518: Software Discovery
  - T1518.001: Security Software Discovery

Collection:
- T1560: Archive Collected Data
  - T1560.001: Archive via Utility
  - T1560.002: Archive via Library
- T1113: Screen Capture
- T1074: Data Staged
  - T1074.001: Local Data Staging
  - T1074.002: Remote Data Staging

Command and Control:
- T1071: Application Layer Protocol
  - T1071.001: Web Protocols (HTTP/HTTPS)
  - T1071.002: File Transfer Protocols
  - T1071.003: Mail Protocols
- T1105: Ingress Tool Transfer
- T1090: Proxy
  - T1090.001: Internal Proxy
  - T1090.002: External Proxy
  - T1090.003: Multi-hop Proxy
- T1571: Non-Standard Port
- T1572: Protocol Tunneling

Exfiltration:
- T1041: Exfiltration Over C2 Channel
- T1567: Exfiltration Over Web Service
  - T1567.001: Exfiltration to Code Repository
  - T1567.002: Exfiltration to Cloud Storage
  - T1567.003: Exfiltration to Text Storage Sites
- T1048: Exfiltration Over Alternative Protocol
  - T1048.001: Exfiltration Over Symmetric Encrypted Channel
  - T1048.002: Exfiltration Over Asymmetric Encrypted Channel
  - T1048.003: Exfiltration Over Unencrypted Non-C2 Protocol

Impact:
- T1486: Data Encrypted for Impact (Ransomware)
- T1489: Service Stop
- T1490: Inhibit System Recovery
- T1491: Defacement
  - T1491.001: Internal Defacement
  - T1491.002: External Defacement
- T1485: Data Destruction
- T1499: Endpoint Denial of Service
  - T1499.001: OS Exhaustion Flood
  - T1499.002: Service Exhaustion Flood
  - T1499.003: Application Exhaustion Flood
  - T1499.004: Application or System Exploitation
"""


def create_story_based_labels(events: List[Dict], session_timestamp: str) -> List[Dict]:
    print(f"\n=== Creating Story-Based Labels ===")
    print(f"Total events: {len(events)}")
    print(f"Session type: {LOG_TYPE}")
    print(f"Creating narrative summaries per minute...")
    
    # Group events by minute
    events_by_minute = group_events_by_minute(events)
    
    print(f"Found {len(events_by_minute)} time windows")
    
    session_counters = {"normal": 0, "suspicious": 0}
    stories = []
    minute_keys = sorted(events_by_minute.keys())
    total_minutes = len(minute_keys)
    
    for i, minute_key in enumerate(minute_keys, 1):
        print(f"  Processing minute {i}/{total_minutes}...")
        minute_events = events_by_minute[minute_key]
        
        story = create_minute_story(minute_events, minute_key, session_counters)
        stories.append(story)
        
        if i < total_minutes and GEMINI_API_KEY:
            time.sleep(5)
    
    print(f"✓ Created {len(stories)} story summaries")
    return stories


def group_events_by_minute(events: List[Dict]) -> Dict[str, List[Dict]]:
    grouped = {}
    
    for event in events:
        try:
            ts_value = event.get('timestamp')
            
            if isinstance(ts_value, (int, float)):
                dt = datetime.fromtimestamp(float(ts_value))
            elif isinstance(ts_value, str):
                ts_str = ts_value.replace('Z', '+00:00')
                dt = datetime.fromisoformat(ts_str)
            else:
                continue
            
            minute_key = dt.strftime('%Y-%m-%d %H:%M')
            
            if minute_key not in grouped:
                grouped[minute_key] = []
            grouped[minute_key].append(event)
        except Exception:
            continue
    
    return grouped


def create_minute_story(events: List[Dict], minute_key: str, session_counters: Dict[str, int]) -> Dict:
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        return create_fallback_story(events, minute_key, session_counters)
    
    try:
        event_summary = summarize_events(events)
        
        prompt = f"""You are a cybersecurity analyst creating a narrative log summary.

Analyze these log events and determine if the activity is truly suspicious or normal.

Time Window: {minute_key}
Number of Events: {len(events)}
Log File Label: {LOG_TYPE} (but contains BOTH normal and suspicious activities - analyze honestly!)

Event Summary (all 3 log types):
{event_summary}

{MITRE_REFERENCE if LOG_TYPE == 'attack' else ''}

CRITICAL: Do NOT force-label everything as suspicious just because the file is labeled "{LOG_TYPE}".
Most activities will be NORMAL. Only mark "suspicious" for clear attack indicators:
- Malicious executables (mimikatz, ransomware, keyloggers)  
- PowerShell with encoded commands, suspicious scripts
- Credential dumping, privilege escalation
- Data exfiltration to unusual external IPs
- C2 communication patterns
- Suspicious registry mods, file encryption

Mark as NORMAL for routine work:
- Regular browsing (github, news, work sites)
- Standard processes (chrome, slack, vscode, system services)
- Normal network (DNS, HTTPS to known sites)
- Expected file operations

Create a narrative description that:
1. COMBINES all three log types (network, system, browser) into ONE coherent story
2. Honestly assesses the activity - do NOT force suspicious labels
3. Mark "suspicious" ONLY if you see clear attack indicators (malicious processes, encoded commands, unusual exfiltration, C2 traffic)
4. Mark "normal" for routine activities (regular browsing, standard processes like chrome/slack, normal network traffic)
5. Be specific but concise (2-4 sentences)

IMPORTANT: This "{LOG_TYPE}" log contains BOTH normal and suspicious activities. Analyze honestly and perfectly.

Respond in JSON format:
{{
    "label": "normal" or "suspicious" (based on ACTUAL behavior, not forced),
    "mitre": "T1XXX.XXX (Technique) ONLY if truly suspicious, empty string if normal",
    "text": "Narrative covering network, system, and browser activities"
}}"""

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(response_text)
        
        if LOG_TYPE.lower() == 'normal':
            label = 'normal'
        else:
            label = result.get('label', 'normal')
            if label not in ['normal', 'suspicious']:
                label = 'suspicious' if result.get('mitre') else 'normal'
        
        session_counters[label] += 1
        return {
            "timestamp": minute_key,
            "session": f"{label}{session_counters[label]}",
            "label": label,
            "mitre": result.get('mitre', '') if label == 'suspicious' else '',
            "text": result.get('text', 'Activity recorded')
        }
        
    except Exception as e:
        print(f"    Error with Gemini: {e}, using fallback...")
        return create_fallback_story(events, minute_key, session_counters)


def summarize_events(events: List[Dict]) -> str:
    summary_parts = []
    
    network_count = sum(1 for e in events if e.get('event_type') == 'network')
    system_count = sum(1 for e in events if e.get('event_type') == 'system')
    browser_count = sum(1 for e in events if e.get('event_type') == 'browser')
    
    summary_parts.append(f"Total: {len(events)} events ({network_count} network, {system_count} system, {browser_count} browser)\n")
    if network_count:
        network_events = [e for e in events if e.get('event_type') == 'network'][:10]
        protocols = [str(e.get('protocol')) for e in network_events if e.get('protocol')]
        destinations = [str(e.get('dst_ip')) for e in network_events if e.get('dst_ip')]
        sources = [str(e.get('src_ip')) for e in network_events if e.get('src_ip')]
        
        protocols_str = ', '.join(sorted(set(protocols))[:5]) if protocols else 'various'
        unique_dests = list(dict.fromkeys(destinations))[:5]
        unique_sources = list(dict.fromkeys(sources))[:3]
        
        summary_parts.append(f"NETWORK: {network_count} packets")
        summary_parts.append(f"  - Protocols: {protocols_str}")
        summary_parts.append(f"  - Source IPs: {', '.join(unique_sources)}")
        summary_parts.append(f"  - Destination IPs: {', '.join(unique_dests)}")
    
    if system_count:
        system_events = [e for e in events if e.get('event_type') == 'system'][:15]
        processes = []
        activities = []
        
        for e in system_events:
            proc = e.get('process_name') or e.get('process') or e.get('ProcessName')
            
            if not proc and e.get('message'):
                msg = str(e.get('message', ''))
                for line in msg.split('\n'):
                    if line.strip().startswith('Image:'):
                        image_path = line.split('Image:')[1].strip()
                        proc = image_path.split('\\')[-1]
                        break
            
            if proc and str(proc).strip():
                processes.append(str(proc)[:50])
            
            if e.get('message'):
                msg = str(e.get('message', ''))
                if 'File creation' in msg:
                    activities.append('File creation')
                elif 'Process Create' in msg:
                    activities.append('Process creation')
                elif 'Network connection' in msg:
                    activities.append('Network connection')
                elif 'Registry' in msg:
                    activities.append('Registry modification')
        
        unique_procs = list(dict.fromkeys(processes))[:7]
        unique_activities = list(dict.fromkeys(activities))[:4]
        
        summary_parts.append(f"\nSYSTEM: {system_count} events")
        if unique_procs:
            summary_parts.append(f"  - Processes: {', '.join(unique_procs)}")
        if unique_activities:
            summary_parts.append(f"  - Activities: {', '.join(unique_activities)}")
        if not unique_procs and not unique_activities:
            summary_parts.append(f"  - Various system activities")
    
    if browser_count:
        browser_events = [e for e in events if e.get('event_type') == 'browser'][:10]
        urls = []
        titles = []
        for e in browser_events:
            if e.get('url'):
                url_str = str(e.get('url'))
                urls.append(url_str[:70])
            
            if e.get('title'):
                title_str = str(e.get('title'))
                titles.append(title_str[:60])
        
        summary_parts.append(f"\nBROWSER: {browser_count} page views")
        if urls:
            summary_parts.append(f"  - URLs: {', '.join(urls[:4])}")
        if titles:
            summary_parts.append(f"  - Titles: {', '.join(titles[:3])}")
        if not urls and not titles:
            summary_parts.append(f"  - Various browser activities")
    
    return '\n'.join(summary_parts) if summary_parts else "Mixed activity across network, system, and browser"


def create_fallback_story(events: List[Dict], minute_key: str, session_counters: Dict[str, int]) -> Dict:
    event_types = {}
    for e in events:
        et = e.get('event_type', 'unknown')
        event_types[et] = event_types.get(et, 0) + 1
    
    parts = []
    if event_types.get('network'):
        parts.append(f"{event_types['network']} network packets")
    if event_types.get('system'):
        parts.append(f"{event_types['system']} system events")
    if event_types.get('browser'):
        parts.append(f"{event_types['browser']} browser activities")
    
    text = f"Recorded {', '.join(parts) if parts else 'system activity'} during this time window."
    
    label = 'normal'
    session_counters[label] += 1
    
    return {
        "timestamp": minute_key,
        "session": f"{label}{session_counters[label]}",
        "label": label,
        "mitre": "",
        "text": text
    }
