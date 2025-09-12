import sys
import os
import requests
from datetime import datetime, timedelta
import json
import pytz

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
        response = requests.get(f"{API_BASE}/buckets")
        response.raise_for_status()
        return list(response.json().keys())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching buckets: {e}")
        return []

def fetch_browser_logs(bucket_id, start_time, end_time, output_folder, timestamp):
    api_url = f"{API_BASE}/buckets/{bucket_id}/events"
    
    print(f"start_time: {start_time}, end_time: {end_time}")
    
    try:
        if isinstance(start_time, str):
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
        else:
            start_dt = start_time.astimezone(pytz.UTC) 
        
        if isinstance(end_time, str):
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
        else:
            end_dt = end_time.astimezone(pytz.UTC)  
            
        print(f"Fetching logs from {start_dt} to {end_dt}")
        
        response = requests.get(api_url)
        response.raise_for_status()
        events = response.json()
        
        print(f"Total events in bucket: {len(events)}")
        
        # If no time filter specified or if we want recent data, get the latest events
        if not events:
            print("No events found in bucket")
            filtered_events = []
        else:
            # Get latest events (ActivityWatch stores events in chronological order)
            # For recent monitoring, get events from the last hour or specified time range
            latest_events = events[-100:]  # Get last 100 events as a sample
            
            filtered_events = []
            for event in events:
                try:
                    event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
                    if start_dt <= event_time <= end_dt:
                        filtered_events.append(event)
                except (ValueError, KeyError) as e:
                    print(f"Error parsing event timestamp: {e}")
                    continue
        
        print(f"Filtered events: {len(filtered_events)}")
        
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{bucket_id}_logs_{timestamp}.json")
        
        # If no filtered events but we have events in bucket, save recent ones
        if not filtered_events and events:
            print("No events in time range, saving recent events instead...")
            recent_events = events[-50:]  # Last 50 events
            with open(output_file, "w") as f:
                json.dump(recent_events, f, indent=4)
            print(f"Recent browser logs saved to {output_file} ({len(recent_events)} events)")
        else:
            with open(output_file, "w") as f:
                json.dump(filtered_events, f, indent=4)
            print(f"Browser logs saved to {output_file} ({len(filtered_events)} events)")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching browser logs: {e}")
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{bucket_id}_logs_{timestamp}_error.json")
        with open(output_file, "w") as f:
            json.dump({"error": str(e)}, f)
    except ValueError as e:
        print(f"Error parsing timestamps: {e}")
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{bucket_id}_logs_{timestamp}_error.json")
        with open(output_file, "w") as f:
            json.dump({"error": f"Timestamp parsing error: {str(e)}"}, f)
            
                  
def main():
    if len(sys.argv) == 4:
        output_folder = sys.argv[1]
        timestamp = sys.argv[2]
        interval_minutes = int(sys.argv[3])
        # Use current time for better data retrieval
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=interval_minutes)
    else:
        print("No arguments provided, running with environment variables...")
        output_folder = get_env_or_fail("BROWSER_LOGS_DIR")
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        interval_minutes = int(get_env_or_fail("BROWSER_LOGS_INTERVAL_MINUTES"))
        # Get data from the last interval_minutes
        end_time = now
        start_time = now - timedelta(minutes=interval_minutes)

    print(f"Time range: {start_time} to {end_time}")

    buckets = get_available_buckets()
    if not buckets:
        print("No buckets found. Is ActivityWatch running?")
        sys.exit(1)

    print("Available buckets:", buckets)

    bucket_id = None
    for b in buckets:
        if b.startswith("aw-watcher-web-chrome") or b.startswith("aw-watcher-web-firefox"):
            bucket_id = b
            break

    if not bucket_id:
        print("No supported browser watcher found (expected -firefox or -chrome).")
        sys.exit(1)

    fetch_browser_logs(bucket_id, start_time, end_time, output_folder, timestamp)

if __name__ == "__main__":
    main()