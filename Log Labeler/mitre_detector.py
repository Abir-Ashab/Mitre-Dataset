"""MITRE ATT&CK detection using Gemini AI - Story-based approach."""
import os
import json
import time
from typing import Dict, List
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LOG_TYPE = os.getenv('LOG_TYPE', 'normal')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# MITRE ATT&CK technique reference for context
MITRE_REFERENCE = """
Common MITRE ATT&CK Techniques:
- T1059.001: PowerShell execution
- T1059.003: Windows Command Shell
- T1041: Exfiltration Over C2 Channel
- T1567.002: Exfiltration to Cloud Storage
- T1083: File and Directory Discovery
- T1082: System Information Discovery
- T1016: System Network Configuration Discovery
- T1555.003: Credentials from Web Browsers
- T1003.001: LSASS Memory dumping
- T1053.005: Scheduled Task
- T1547.001: Registry Run Keys
- T1070.001: Clear Windows Event Logs
- T1562.001: Disable or Modify Tools
- T1204.002: Malicious File execution
- T1486: Data Encrypted for Impact (Ransomware)
"""


def create_story_based_labels(events: List[Dict], session_timestamp: str) -> List[Dict]:
    """
    Create story-based labels for log events grouped by time windows.
    Instead of labeling each event, creates narrative summaries per minute.
    
    Args:
        events: List of all log events
        session_timestamp: Original session timestamp (e.g., "20250912_105900")
        
    Returns:
        List of 20 story objects, one per minute
    """
    print(f"\n=== Creating Story-Based Labels ===")
    print(f"Total events: {len(events)}")
    print(f"Session type: {LOG_TYPE}")
    print(f"Creating narrative summaries per minute...")
    
    # Group events by minute
    events_by_minute = group_events_by_minute(events)
    
    print(f"Found {len(events_by_minute)} time windows")
    
    # Track session counters for dynamic naming
    session_counters = {"normal": 0, "suspicious": 0}
    
    # Create story for each minute (up to 20 minutes)
    stories = []
    minute_keys = sorted(events_by_minute.keys())[:20]  # Take first 20 minutes
    
    for i, minute_key in enumerate(minute_keys, 1):
        print(f"  Processing minute {i}/20...")
        minute_events = events_by_minute[minute_key]
        
        story = create_minute_story(minute_events, minute_key, session_counters)
        stories.append(story)
        
        # Rate limiting: wait between requests to stay under 15/min
        if i < len(minute_keys) and GEMINI_API_KEY:
            time.sleep(5)  # 5 seconds between requests = 12 requests/min (safe)
    
    # If less than 20 minutes, fill remaining with empty stories
    while len(stories) < 20:
        session_counters["normal"] += 1
        stories.append({
            "timestamp": "",
            "session": f"normal{session_counters['normal']}",
            "label": "normal",
            "mitre": "",
            "text": "No activity recorded in this time window"
        })
    
    print(f"✓ Created {len(stories)} story summaries")
    return stories


def group_events_by_minute(events: List[Dict]) -> Dict[str, List[Dict]]:
    """Group events into 1-minute time windows - handling multiple timestamp formats."""
    grouped = {}
    
    for event in events:
        try:
            ts_value = event.get('timestamp')
            
            # Handle different timestamp formats
            if isinstance(ts_value, (int, float)):
                # Unix timestamp (network events)
                dt = datetime.fromtimestamp(float(ts_value))
            elif isinstance(ts_value, str):
                # ISO format string (browser and system events)
                # Replace Z with +00:00 for proper parsing
                ts_str = ts_value.replace('Z', '+00:00')
                dt = datetime.fromisoformat(ts_str)
            else:
                continue
            
            minute_key = dt.strftime('%Y-%m-%d %H:%M')
            
            if minute_key not in grouped:
                grouped[minute_key] = []
            grouped[minute_key].append(event)
        except Exception as e:
            # Skip events with invalid timestamps
            continue
    
    return grouped


def create_minute_story(events: List[Dict], minute_key: str, session_counters: Dict[str, int]) -> Dict:
    """
    Create a story narrative for events in a single minute using Gemini AI.
    
    Args:
        events: Events in this minute
        minute_key: Time window key (e.g., "2025-09-12 10:59")
        session_counters: Dict tracking count of normal and suspicious sessions
        
    Returns:
        Story object with narrative description
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        return create_fallback_story(events, minute_key, session_counters)
    
    try:
        # Summarize events for the prompt (don't send all details)
        event_summary = summarize_events(events)
        
        # Create prompt for Gemini
        prompt = f"""You are a cybersecurity analyst creating a narrative log summary.

Analyze ALL types of log events (network, system, and browser) from this {LOG_TYPE} session and create a comprehensive story.

Time Window: {minute_key}
Number of Events: {len(events)}
Session Type: {LOG_TYPE}

Event Summary (covering all 3 log types):
{event_summary}

{MITRE_REFERENCE if LOG_TYPE == 'attack' else ''}

Create a narrative description that:
1. COMBINES all three log types (network traffic, system processes, and browser activity) into one coherent story
2. Describes what the user/system was doing during this minute across ALL activities
3. For {"attack" if LOG_TYPE == "attack" else "normal"} sessions, {"identify if the COMBINED activity is suspicious (attack behavior) or normal, and identify MITRE IDs if suspicious" if LOG_TYPE == "attack" else "describe the normal activities comprehensively"}
4. Connect related activities (e.g., browser visiting URL → network connection → system process)
5. Be specific but concise (2-4 sentences covering network, system, and browser)

Example format:
- "User browsed to example.com, triggering 45 network packets to IP 192.168.1.1. System process chrome.exe handled the connection. Browser recorded page load activities."

Respond in JSON format:
{{
    "label": "{"suspicious or normal (based on activity)" if LOG_TYPE == "attack" else "normal"}",
    "mitre": "{"T1XXX.XXX (Technique Name) if suspicious, empty string if normal" if LOG_TYPE == "attack" else ""}",
    "text": "Comprehensive narrative covering network, system, and browser activities"
}}"""

        # Call Gemini API
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(response_text)
        
        # Determine label - for normal logs, always "normal"; for attack logs, dynamic
        if LOG_TYPE == 'normal':
            label = 'normal'
        else:  # attack
            label = result.get('label', 'normal')
            if label not in ['normal', 'suspicious']:
                label = 'suspicious' if result.get('mitre') else 'normal'
        
        # Update session counter
        session_counters[label] += 1
        
        # Build story object with dynamic session naming
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
    """Create a concise summary of events for the AI prompt - covering all 3 log types."""
    summary_parts = []
    
    # Count event types
    network_count = sum(1 for e in events if e.get('event_type') == 'network')
    system_count = sum(1 for e in events if e.get('event_type') == 'system')
    browser_count = sum(1 for e in events if e.get('event_type') == 'browser')
    
    # Header
    summary_parts.append(f"Total: {len(events)} events ({network_count} network, {system_count} system, {browser_count} browser)\n")
    
    # Network details
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
    
    # System details
    if system_count:
        system_events = [e for e in events if e.get('event_type') == 'system'][:15]
        processes = []
        activities = []
        
        for e in system_events:
            # Try to get process name
            proc = e.get('process_name') or e.get('process') or e.get('ProcessName')
            
            # Extract from Sysmon message format
            if not proc and e.get('message'):
                msg = str(e.get('message', ''))
                # Extract Image: field (contains full process path)
                for line in msg.split('\n'):
                    if line.strip().startswith('Image:'):
                        image_path = line.split('Image:')[1].strip()
                        proc = image_path.split('\\')[-1]  # Get just filename
                        break
            
            if proc and str(proc).strip():
                processes.append(str(proc)[:50])
            
            # Extract activity type from message
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
    
    # Browser details
    if browser_count:
        browser_events = [e for e in events if e.get('event_type') == 'browser'][:10]
        urls = []
        titles = []
        for e in browser_events:
            # Direct url field
            if e.get('url'):
                url_str = str(e.get('url'))
                urls.append(url_str[:70])
            
            # Direct title field
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
    """Create a basic story without AI when Gemini is unavailable."""
    event_types = {}
    for e in events:
        et = e.get('event_type', 'unknown')
        event_types[et] = event_types.get(et, 0) + 1
    
    # Build simple description
    parts = []
    if event_types.get('network'):
        parts.append(f"{event_types['network']} network packets")
    if event_types.get('system'):
        parts.append(f"{event_types['system']} system events")
    if event_types.get('browser'):
        parts.append(f"{event_types['browser']} browser activities")
    
    text = f"Recorded {', '.join(parts) if parts else 'system activity'} during this time window."
    
    # For normal logs, always normal; for attack logs, default to normal in fallback
    label = 'normal'
    session_counters[label] += 1
    
    return {
        "timestamp": minute_key,
        "session": f"{label}{session_counters[label]}",
        "label": label,
        "mitre": "",
        "text": text
    }


# Legacy function for compatibility (not used in story mode)
def label_event(event: Dict) -> Dict:
    """Legacy single-event labeling (not used in story mode)."""
    event['label'] = LOG_TYPE
    event['mitre_techniques'] = []
    event['reasoning'] = 'Story-based labeling - see summary'
    return event
