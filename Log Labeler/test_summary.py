"""Test script to verify the summarize_events function properly extracts all 3 log types."""
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))
from mitre_detector import summarize_events, group_events_by_minute

# Load the sample log file
log_file = r"c:\Users\MSI\Downloads\text_log_20250912_111900.json"

with open(log_file, 'r', encoding='utf-8') as f:
    events = json.load(f)

print(f"Total events loaded: {len(events)}")
print(f"=" * 80)

# Group by minute
events_by_minute = group_events_by_minute(events)
print(f"\nTotal time windows: {len(events_by_minute)}")

# Show first 3 minutes
minute_keys = sorted(events_by_minute.keys())[:3]

for i, minute_key in enumerate(minute_keys, 1):
    minute_events = events_by_minute[minute_key]
    print(f"\n{'=' * 80}")
    print(f"MINUTE {i}: {minute_key}")
    print(f"{'=' * 80}")
    print(f"Total events in this minute: {len(minute_events)}")
    print()
    
    # Generate summary
    summary = summarize_events(minute_events)
    print(summary)
    print()
