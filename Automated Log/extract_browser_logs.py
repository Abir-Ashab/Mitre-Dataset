import sys
import os
import requests
from datetime import datetime, timedelta
import json
import pytz
from upload_to_gdrive import upload_file_from_content

LOCAL_OFFSET = 6  # Same offset as syslogs script

def get_env_or_fail(var):
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value

API_BASE = get_env_or_fail("BROWSER_API_BASE")

def get_available_buckets():
    """Fetch list of available buckets from ActivityWatch."""
    try:
        response = requests.get(f"{API_BASE}/buckets", timeout=5)
        response.raise_for_status()
        return list(response.json().keys())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to ActivityWatch: {e}")
        print("⚠️  ActivityWatch might not be running or responding")
        print("   Please check if ActivityWatch is started")
        return []

def fetch_browser_logs(bucket_id, start_time, end_time, folder_id, timestamp):
    api_url = f"{API_BASE}/buckets/{bucket_id}/events"
    
    print(f"start_time: {start_time}, end_time: {end_time}")
    
    try:
        # Convert times to UTC for comparison with ActivityWatch timestamps
        if isinstance(start_time, str):
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        else:
            start_dt = start_time
            
        if isinstance(end_time, str):
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        else:
            end_dt = end_time
        
        # ActivityWatch stores in local time, so we don't need UTC conversion
        print(f"Fetching logs from {start_dt} to {end_dt}")
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        events = response.json()
        
        print(f"Total events in bucket: {len(events)}")
        
        # If no time filter specified or if we want recent data, get the latest events
        if not events:
            print("No events found in bucket")
            filtered_events = []
        else:
            filtered_events = []
            print(f"Searching for events between {start_dt} and {end_dt}")
            
            # Debug: show the latest few event timestamps
            if len(events) > 0:
                print(f"Latest event timestamp: {events[-1]['timestamp']}")
                print(f"Oldest event timestamp: {events[0]['timestamp']}")
            
            event_count_checked = 0
            for event in events:
                event_count_checked += 1
                try:
                    # Parse ActivityWatch timestamp (ISO format)
                    event_timestamp = event["timestamp"]
                    if event_timestamp.endswith("Z"):
                        event_timestamp = event_timestamp[:-1] + "+00:00"
                    
                    event_time = datetime.fromisoformat(event_timestamp)
                    # Convert UTC to local time for comparison
                    event_time_local = event_time.replace(tzinfo=pytz.UTC).astimezone().replace(tzinfo=None)
                    
                    if start_dt <= event_time_local <= end_dt:
                        filtered_events.append(event)
                        if len(filtered_events) <= 3:  # Debug first few matches
                            print(f"Found matching event: {event_time_local} (original: {event_time})")
                            
                except (ValueError, KeyError) as e:
                    print(f"Error parsing event timestamp: {e}")
                    continue
            
            print(f"Checked {event_count_checked} events, found {len(filtered_events)} matches")
        
        print(f"Filtered events: {len(filtered_events)}")
        
        filename = f"{bucket_id}_logs_{timestamp}.json"
        
        # If no filtered events, get recent events from around the time period
        if not filtered_events:
            print("❌ No browser events found in exact time range")
            print("⚠️  This likely means:")
            print("   - No browser activity during this time")
            print("   - ActivityWatch browser watcher not running")
            print("   - Browser was closed during monitoring")
            
            # Check if the latest event is very old
            if events:
                latest_timestamp = events[-1]['timestamp']
                latest_time = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
                latest_local = latest_time.replace(tzinfo=pytz.UTC).astimezone().replace(tzinfo=None)
                age_hours = (datetime.now() - latest_local).total_seconds() / 3600
                
                if age_hours > 1:
                    print(f"⚠️  Latest browser event is {age_hours:.1f} hours old")
                    print("   Consider restarting ActivityWatch browser watcher")
            
            # Create empty log file to indicate no activity
            empty_log = {
                "note": "No browser events found in time range",
                "search_range": f"{start_dt} to {end_dt}",
                "latest_available_event": events[-1]['timestamp'] if events else "No events",
                "reason": "Browser watcher not collecting data or no browser activity",
                "events": []
            }
            
            json_content = json.dumps(empty_log, indent=4)
            upload_file_from_content(json_content, folder_id, filename, 'application/json')
            print(f"Empty browser log uploaded (no activity detected): {filename}")
        else:
            json_content = json.dumps(filtered_events, indent=4)
            upload_file_from_content(json_content, folder_id, filename, 'application/json')
            print(f"✓ Browser logs uploaded: {filename} ({len(filtered_events)} events from exact time range)")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching browser logs: {e}")
        print("⚠️  ActivityWatch connection failed")
        print("   Please check if ActivityWatch is running")
        
        # Create error log file
        error_filename = f"{bucket_id if 'bucket_id' in locals() else 'browser'}_logs_{timestamp}_connection_error.json"
        error_content = json.dumps({
            "error": "ActivityWatch connection failed",
            "details": str(e),
            "timestamp": timestamp,
            "search_range": f"{start_dt} to {end_dt}",
            "note": "ActivityWatch was not responding during log extraction"
        }, indent=4)
        upload_file_from_content(error_content, folder_id, error_filename, 'application/json')
        print(f"Error log uploaded: {error_filename}")
        
    except ValueError as e:
        print(f"❌ Error parsing timestamps: {e}")
        error_filename = f"{bucket_id if 'bucket_id' in locals() else 'browser'}_logs_{timestamp}_parsing_error.json"
        error_content = json.dumps({
            "error": "Timestamp parsing error", 
            "details": str(e),
            "timestamp": timestamp
        }, indent=4)
        upload_file_from_content(error_content, folder_id, error_filename, 'application/json')
        print(f"Error log uploaded: {error_filename}")
            
                  
def main():
    if len(sys.argv) == 4:
        folder_id = sys.argv[1]  # Now Google Drive folder ID
        timestamp = sys.argv[2]
        interval_minutes = int(sys.argv[3])
        
        # Calculate time range based on the timestamp, similar to syslogs
        interval_start_local = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
        # Use the actual interval time, not current time
        start_time = interval_start_local
        end_time = interval_start_local + timedelta(minutes=interval_minutes)
    else:
        print("Error: This script now requires Google Drive folder ID")
        print("Run from main.py for proper integration")
        sys.exit(1)

    print(f"Time range: {start_time} to {end_time}")

    buckets = get_available_buckets()
    if not buckets:
        print("No buckets found. Is ActivityWatch running?")
        sys.exit(1)

    print("Available buckets:", buckets)

    bucket_id = None
    browser_buckets = []
    
    # Find all browser watcher buckets
    for b in buckets:
        if "aw-watcher-web-chrome" in b or "aw-watcher-web-firefox" in b:
            browser_buckets.append(b)
    
    if browser_buckets:
        # If multiple browser buckets, choose the one with most recent activity
        if len(browser_buckets) > 1:
            print(f"Found multiple browser buckets: {browser_buckets}")
            # Test which bucket has recent data by checking latest event
            latest_bucket = None
            latest_time = None
            
            for bucket in browser_buckets:
                try:
                    test_response = requests.get(f"{API_BASE}/buckets/{bucket}/events?limit=1")
                    test_events = test_response.json()
                    if test_events:
                        event_time = test_events[0]['timestamp']
                        if latest_time is None or event_time > latest_time:
                            latest_time = event_time
                            latest_bucket = bucket
                except:
                    continue
            
            bucket_id = latest_bucket if latest_bucket else browser_buckets[0]
        else:
            bucket_id = browser_buckets[0]
        
        print(f"Using browser bucket: {bucket_id}")
    
    # Fallback to window watcher if browser watcher not available
    if not bucket_id:
        for b in buckets:
            if "aw-watcher-window" in b:
                bucket_id = b
                print(f"⚠️  Browser watcher not found, using window watcher: {bucket_id}")
                break

    if not bucket_id:
        print("❌ No supported watcher found (browser or window).")
        sys.exit(1)

    fetch_browser_logs(bucket_id, start_time, end_time, folder_id, timestamp)

if __name__ == "__main__":
    main()