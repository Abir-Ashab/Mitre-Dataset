#!/usr/bin/env python3
"""remove_by_event_id.py

Usage:
  python remove_by_event_id.py <filename> [--dry-run] [--out <outfile>]

Note:
  Event ID(s) to remove are hardcoded in the script via the HARDCODED_EVENT_IDS set.
  Edit the HARDCODED_EVENT_IDS set in the script to change which event IDs are removed.

Removes any log objects whose `winlog.event_id` matches one of the hardcoded event IDs.
Works when the file contains either a top-level list of logs or a dict with a `logs` list.
"""
import argparse
import json
import os
import sys
from copy import deepcopy


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


def normalize_event_id(x):
    if x is None:
        return ""
    return str(x).strip()


def main():
    p = argparse.ArgumentParser(description="Remove JSON log objects by hardcoded winlog.event_id(s)")
    p.add_argument("filename", help="Path to the input JSON file")
    p.add_argument("--dry-run", action="store_true", help="Don't write output, only print what would be removed")
    p.add_argument("--out", help="Output filename (default: add _filtered before ext)")
    args = p.parse_args()

    # Hardcoded event IDs to remove — edit this set as needed
    HARDCODED_EVENT_IDS = {"5379"}

    if not os.path.exists(args.filename):
        print(f"File not found: {args.filename}")
        sys.exit(1)

    data = load_json_file(args.filename)

    # locate logs
    if isinstance(data, dict) and "logs" in data and isinstance(data["logs"], list):
        logs = data["logs"]
        container_type = "dict"
    elif isinstance(data, list):
        logs = data
        container_type = "list"
    else:
        print("No logs list found in the provided JSON file.")
        sys.exit(1)

    targets = set(normalize_event_id(e) for e in HARDCODED_EVENT_IDS)

    total = len(logs)
    removed = 0
    kept = []

    for item in logs:
        event_id = None
        try:
            event_id = normalize_event_id(item.get("winlog", {}).get("event_id"))
        except Exception:
            event_id = ""

        if event_id in targets:
            removed += 1
        else:
            kept.append(item)

    print(f"Found {total} logs; {removed} will be removed (matching {sorted(targets)}).")

    if args.dry_run:
        print("Dry run enabled — no file will be written.")
        sys.exit(0)

    # prepare output structure using deep copies to avoid mutating the original in-memory data
    if container_type == "dict":
        out_data = deepcopy(data)
        out_data["logs"] = deepcopy(kept)
    else:
        out_data = deepcopy(kept)

    def make_non_overwriting_filename(input_path, suffix="_filtered"):
        base, ext = os.path.splitext(input_path)
        candidate = base + suffix + ext
        i = 1
        while os.path.exists(candidate) or os.path.abspath(candidate) == os.path.abspath(input_path):
            candidate = f"{base}{suffix}_{i}{ext}"
            i += 1
        return candidate

    if args.out:
        out_filename = args.out
        if os.path.abspath(out_filename) == os.path.abspath(args.filename):
            out_filename = make_non_overwriting_filename(args.filename)
            print(f"Provided output filename equals input; will write to {out_filename} instead to avoid overwriting the original.")
        elif os.path.exists(out_filename):
            # avoid overwriting the provided path
            out_filename = make_non_overwriting_filename(out_filename, suffix="_filtered")
            print(f"Provided output file already exists; writing to {out_filename} instead to avoid overwriting.")
    else:
        out_filename = make_non_overwriting_filename(args.filename)

    with open(out_filename, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(kept)} logs to {out_filename} (removed {removed}). Original file left intact.")


if __name__ == "__main__":
    main()
