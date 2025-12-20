#!/usr/bin/env python3
"""list_unique_process_names.py

Usage:
  python list_unique_process_names.py <filename> [--counts] [--ignore-case]

Prints all unique `ProcessName` values found in the file's logs (works when file is a list of logs
or a dict containing a `logs` list).

Options:
  --counts       Show counts for each ProcessName, sorted by count desc
  --ignore-case  Treat ProcessName values case-insensitively when de-duplicating
"""
import argparse
import json
import os
import sys
from collections import Counter


def load_json_file(path):
    encodings = [("utf-8", "strict"), ("utf-8", "replace"), ("cp1252", "replace")]
    for enc, errors in encodings:
        try:
            with open(path, "r", encoding=enc, errors=errors) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
    print(f"Failed to read file with supported encodings: {path}")
    sys.exit(1)


def extract_process_name(item):
    try:
        return item.get("winlog", {}).get("event_data", {}).get("ProcessName")
    except Exception:
        return None


def normalize(name, ignore_case=False):
    if not isinstance(name, str):
        return None
    n = name.strip().strip('"')
    if ignore_case:
        return n.lower()
    return n


def main():
    p = argparse.ArgumentParser(description="List unique ProcessName values from annotated logs")
    p.add_argument("filename", help="Path to JSON file containing logs or a dict with a `logs` list")
    p.add_argument("--counts", action="store_true", help="Show counts for each ProcessName")
    p.add_argument("--ignore-case", action="store_true", help="Ignore case when deduplicating ProcessName values")
    args = p.parse_args()

    if not os.path.exists(args.filename):
        print(f"File not found: {args.filename}")
        sys.exit(1)

    data = load_json_file(args.filename)

    # locate logs
    if isinstance(data, dict) and "logs" in data and isinstance(data["logs"], list):
        logs = data["logs"]
    elif isinstance(data, list):
        logs = data
    else:
        print("No logs list found in the provided JSON file.")
        sys.exit(1)

    counter = Counter()
    seen_examples = {}

    for item in logs:
        pname = extract_process_name(item)
        norm = normalize(pname, ignore_case=args.ignore_case)
        if norm:
            counter[norm] += 1
            # remember an example original spelling for display (preserve case)
            if norm not in seen_examples:
                seen_examples[norm] = pname.strip()

    if not counter:
        print("No ProcessName values found in the logs.")
        sys.exit(0)

    if args.counts:
        # sort by count desc then name
        for name, cnt in counter.most_common():
            display = seen_examples.get(name, name)
            print(f"{cnt:6d}  {display}")
    else:
        for name in sorted(seen_examples.values()):
            print(name)


if __name__ == "__main__":
    main()
