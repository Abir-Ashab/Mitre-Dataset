"""MITRE ATT&CK detection using Gemini AI analyzing full system logs."""
import os
import json
import time
from typing import Dict, List
from datetime import datetime, timedelta
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


def create_story_based_labels(events: List[Dict], session_timestamp: str, window_size_seconds: int = 60) -> List[Dict]:
    print(f"\n=== Analyzing Log Events ===")
    print(f"Total events: {len(events)}")
    print(f"Session type: {LOG_TYPE}")
    print(f"Processing logs in {window_size_seconds}-second windows...")
    
    events_by_window = group_events_by_time_window(events, window_size_seconds)
    
    print(f"Found {len(events_by_window)} time windows")
    
    session_counters = {"normal": 0, "suspicious": 0}
    analysis_results = []
    window_keys = sorted(events_by_window.keys())
    total_windows = len(window_keys)
    
    for i, window_key in enumerate(window_keys, 1):
        print(f"  Processing window {i}/{total_windows} ({window_key})...")
        window_events = events_by_window[window_key]
        
        result = analyze_minute_events(window_events, window_key, session_counters)
        analysis_results.append(result)
        
        if i < total_windows and GEMINI_API_KEY:
            time.sleep(5)
    
    print(f"✓ Completed analysis of {len(analysis_results)} time windows")
    return analysis_results


def group_events_by_time_window(events: List[Dict], window_size_seconds: int = 60) -> Dict[str, List[Dict]]:
    """
    Group events into time windows of specified size.
    
    Args:
        events: List of event dictionaries
        window_size_seconds: Size of each time window in seconds (default: 60 seconds)
    
    Returns:
        Dictionary mapping time window start times to lists of events
    """
    grouped = {}
    start_time = None
    
    # First, find the start time
    for event in events:
        if not isinstance(event, dict):
            print(f"Warning: Non-dictionary event found of type {type(event)}")
            continue
            
        try:
            ts_value = event.get('timestamp')
            if ts_value and isinstance(ts_value, str):
                ts_str = ts_value.replace('Z', '+00:00')
                dt = datetime.fromisoformat(ts_str)
                if not start_time or dt < start_time:
                    start_time = dt
        except Exception as e:
            print(f"Warning: Error parsing timestamp: {str(e)}")
            continue
    
    if not start_time:
        return grouped
    
    # Calculate session duration (20 minutes in seconds)
    session_duration = 20 * 60
    end_time = start_time.replace(minute=start_time.minute + 20)
    
    for event in events:
        try:
            ts_value = event.get('timestamp')
            if not ts_value or not isinstance(ts_value, str):
                continue

            ts_str = ts_value.replace('Z', '+00:00')
            dt = datetime.fromisoformat(ts_str)
            
            # Skip events outside our session window
            if dt < start_time or dt >= end_time:
                continue
            
            # Calculate which time window this event belongs to
            seconds_from_start = (dt - start_time).total_seconds()
            window_index = int(seconds_from_start / window_size_seconds)
            window_start = start_time + timedelta(seconds=window_index * window_size_seconds)
            window_end = window_start + timedelta(seconds=window_size_seconds)
            
            # Create a descriptive key that includes the time range
            window_key = f"{window_start.strftime('%Y-%m-%d %H:%M:%S')} - {window_end.strftime('%H:%M:%S')}"
            
            if window_key not in grouped:
                grouped[window_key] = []
            grouped[window_key].append(event)
            
        except Exception as e:
            print(f"Error parsing timestamp '{ts_value}': {str(e)}")
            continue
    
    return grouped


def analyze_minute_events(events: List[Dict], minute_key: str, session_counters: Dict[str, int]) -> Dict:
    
    # Convert any list items to dictionaries with proper format
    sanitized_events = []
    for event in events:
        if isinstance(event, dict):
            sanitized_events.append(event)
        elif isinstance(event, list) and len(event) > 0:
            # Try to convert list to proper event dictionary
            try:
                event_dict = {
                    "event_type": "unknown",
                    "timestamp": minute_key,
                    "message": f"Raw data: {str(event)}"
                }
                # If list has key-value pairs, try to extract them
                if len(event) >= 2 and isinstance(event[0], str):
                    event_dict["event_type"] = event[0]
                sanitized_events.append(event_dict)
            except Exception as e:
                print(f"Warning: Could not convert list event: {str(e)}")
                continue
        else:
            print(f"Warning: Skipping invalid event type: {type(event)}")
            continue

    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        return create_fallback_analysis(sanitized_events, minute_key, session_counters)
    
    try:
        event_logs = format_full_logs(sanitized_events)
        
        prompt = f"""You are a cybersecurity analyst analyzing detailed system logs.

Analyze these log events and determine if the activity is truly suspicious or normal. Keep every detail of the logs, and do NOT omit any log types. 

Time Window: {minute_key}
Number of Events: {len(events)}
Log File Label: {LOG_TYPE} (but contains BOTH normal and suspicious activities - analyze honestly!)

Event logs (all 3 log types):
{event_logs}

{MITRE_REFERENCE if LOG_TYPE == 'suspicious' else ''}

CRITICAL: Do NOT force-label everything as suspicious just because the file is labeled suspicious. Also, when the {LOG_TYPE} is suspicious, it will must contain suspicious activities to be labeled as such. But most activities will be NORMAL. Only mark "suspicious" for clear attack indicators .Mark as NORMAL for routine work:
- Regular browsing (github, news, work sites)
- Standard processes (chrome, slack, vscode, system services)
- Normal network (DNS, HTTPS to known sites)
- Expected file operations

Create a narrative description that:
1. COMBINES all three log types (network, system, browser) into ONE coherent story. You can make several json object for a specific minute if needed. In a specific minute, there could be both normal and suspicious activities. So you must cover both in 2 different json object.
2. Honestly assesses the activity - do NOT force suspicious labels
3. Mark "suspicious" ONLY if you see clear attack indicators (malicious processes, encoded commands, unusual exfiltration, C2 traffic etc many more mitre techniques from the reference)
4. Mark "normal" for routine activities (regular browsing, standard processes like chrome/slack, normal network traffic)
5. Be specific but concise 

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
        
        # More robust response parsing
        try:
            # First try parsing the whole response as JSON
            json_data = json.loads(response_text)
            
            # Handle both single dict and list of dicts
            results = []
            if isinstance(json_data, list):
                # Process all valid JSON objects from the list
                for item in json_data:
                    if isinstance(item, dict) and ('label' in item or 'text' in item):
                        results.append(item)
            else:
                if isinstance(json_data, dict) and ('label' in json_data or 'text' in json_data):
                    results.append(json_data)
                    
            if not results:
                return create_fallback_analysis(events, minute_key, session_counters)
                
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from markdown blocks
            try:
                # Try to find JSON block
                if '```json' in response_text:
                    json_text = response_text.split('```json')[1].split('```')[0].strip()
                elif '```' in response_text:
                    json_text = response_text.split('```')[1].split('```')[0].strip()
                else:
                    # Look for JSON-like content between curly braces
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_text = response_text[start:end]
                    else:
                        raise ValueError("No JSON-like content found")
                
                parsed = json.loads(json_text)
                if isinstance(parsed, list):
                    results = [item for item in parsed if isinstance(item, dict) and ('label' in item or 'text' in item)]
                elif isinstance(parsed, dict) and ('label' in parsed or 'text' in parsed):
                    results = [parsed]
                else:
                    results = []
                    
            except Exception as e:
                print(f"    Failed to parse Gemini response as JSON: {e}")
                return create_fallback_analysis(events, minute_key, session_counters)
        
        if not results:
            print(f"    No valid analysis results found")
            return create_fallback_analysis(events, minute_key, session_counters)
            
        # Process all valid results
        responses = []
        for result in results:
            if LOG_TYPE.lower() == 'normal':
                label = 'normal'
            else:
                label = result.get('label', 'normal')
                if label not in ['normal', 'suspicious']:
                    label = 'suspicious' if result.get('mitre') else 'normal'
            
            session_counters[label] += 1
            responses.append({
                "timestamp": minute_key,
                "session": f"{label}{session_counters[label]}",
                "label": label,
                "mitre": result.get('mitre', '') if label == 'suspicious' else '',
                "text": result.get('text', 'Activity recorded')
            })
        
        # Return all responses for this minute
        return responses[0] if len(responses) == 1 else {
            "timestamp": minute_key,
            "session": "combined",
            "label": "suspicious" if any(r["label"] == "suspicious" for r in responses) else "normal",
            "mitre": "; ".join(filter(None, (r["mitre"] for r in responses))),
            "text": " | ".join(r["text"] for r in responses)
        }
        
    except Exception as e:
        print(f"    Error with Gemini: {e}, using fallback...")
        return create_fallback_analysis(events, minute_key, session_counters)


def format_full_logs(events: List[Dict]) -> str:
    seen = set()
    deduped_events = []
    
    def safe_get(obj, key, default=None):
        """Safely get a value from either a dict or list."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return default
    
    for event in events:
        if not isinstance(event, dict):
            print(f"Warning: Skipping non-dictionary event: {type(event)}")
            continue
            
        event_key = (
            safe_get(event, 'event_type'),
            safe_get(event, 'timestamp'),
            safe_get(event, 'process_name') or safe_get(event, 'process') or safe_get(event, 'ProcessName'),
            safe_get(event, 'url'),
            safe_get(event, 'dst_ip'),
            safe_get(event, 'src_ip'),
            safe_get(event, 'protocol'),
            str(safe_get(event, 'message'))[:200] if safe_get(event, 'message') else None
        )
        if event_key not in seen:
            seen.add(event_key)
            deduped_events.append(event)

    formatted_logs = []
    
    network_count = sum(1 for e in deduped_events if safe_get(e, 'event_type') == 'network')
    system_count = sum(1 for e in deduped_events if safe_get(e, 'event_type') == 'system')
    browser_count = sum(1 for e in deduped_events if safe_get(e, 'event_type') == 'browser')
    formatted_logs.append(f"Total: {len(deduped_events)} unique events ({network_count} network, {system_count} system, {browser_count} browser)\n")

    if network_count:
        formatted_logs.append("NETWORK EVENTS:")
        for event in [e for e in deduped_events if safe_get(e, 'event_type') == 'network']:
            log_entry = []
            if safe_get(event, 'protocol'): log_entry.append(f"Protocol: {safe_get(event, 'protocol')}")
            if safe_get(event, 'src_ip'): log_entry.append(f"Src: {safe_get(event, 'src_ip')}")
            if safe_get(event, 'dst_ip'): log_entry.append(f"Dst: {safe_get(event, 'dst_ip')}")
            if safe_get(event, 'src_port'): log_entry.append(f"SrcPort: {safe_get(event, 'src_port')}")
            if safe_get(event, 'dst_port'): log_entry.append(f"DstPort: {safe_get(event, 'dst_port')}")
            formatted_logs.append("  " + " | ".join(log_entry))

    if system_count:
        formatted_logs.append("\nSYSTEM EVENTS:")
        for event in [e for e in deduped_events if safe_get(e, 'event_type') == 'system']:
            log_entry = []
            proc = safe_get(event, 'process_name') or safe_get(event, 'process') or safe_get(event, 'ProcessName')
            if proc: log_entry.append(f"Process: {proc}")
            msg = safe_get(event, 'message')
            if msg: 
                msg = str(msg)
                msg = ' | '.join(line.strip() for line in msg.split('\n') if line.strip())
                log_entry.append(msg)
            formatted_logs.append("  " + " | ".join(log_entry))

    if browser_count:
        formatted_logs.append("\nBROWSER EVENTS:")
        for event in [e for e in deduped_events if safe_get(e, 'event_type') == 'browser']:
            log_entry = []
            if safe_get(event, 'url'): log_entry.append(f"URL: {safe_get(event, 'url')}")
            if safe_get(event, 'title'): log_entry.append(f"Title: {safe_get(event, 'title')}")
            if safe_get(event, 'type'): log_entry.append(f"Action: {safe_get(event, 'type')}")
            formatted_logs.append("  " + " | ".join(log_entry))

    return '\n'.join(formatted_logs)


def create_fallback_analysis(events: List[Dict], minute_key: str, session_counters: Dict[str, int]) -> Dict:
    event_types = {}
    for e in events:
        if not isinstance(e, dict):
            et = 'unknown'
        else:
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
