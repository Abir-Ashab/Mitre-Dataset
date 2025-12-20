#!/usr/bin/env python3
"""label_by_event_image.py

Usage:
  python label_by_event_image.py <filename> [--dry-run] [--out <outfile>]

Note:
  The filter rules are hardcoded in the FILTER_RULES list below. Each rule is a dict with keys:
    - event_id: string or numeric value to match against winlog.event_id (string comparison)
    - image: image path to match against winlog.event_data.Image (normalized, case-insensitive; basename match allowed)
    - label: label to set (e.g. "suspicious")
    - mitre_techniques: list of technique IDs to set

  Edit FILTER_RULES to add or change rules.

Applies the matching rule(s) to each log (both event_id and image must match) and sets
`label` and `mitre_techniques` on the log. The script never overwrites the input file;
it writes a new file (adds suffix) unless `--out` is provided and safe.
"""
import argparse
import json
import os
import sys
from copy import deepcopy
from typing import List, Dict, Any

# Hardcoded rules — edit these values to change behavior
# Example rule: when event_id == "3" and Image == r"C:\Users\User\AppData\LocalHSoouxEnKa.exe"
# then set label and mitre_techniques as shown.
FILTER_RULES: List[Dict[str, Any]] = [
    {
        "event_id": "3",
        "image": r"C:\\Users\\User\\AppData\\LocalHSoouxEnKa.exe",
        "label": "suspicious",
        "mitre_techniques": ["T1071"],
    }
]


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


def normalize_path(p: str) -> str:
    if not isinstance(p, str):
        return ""
    p = p.strip().strip('"')
    try:
        return os.path.normcase(os.path.normpath(p))
    except Exception:
        return p.strip().lower()


def matches_rule(item: dict, rule: dict) -> bool:
    try:
        event_id = str(item.get("winlog", {}).get("event_id", "")).strip()
        image = item.get("winlog", {}).get("event_data", {}).get("Image")
    except Exception:
        return False

    if not event_id or image is None:
        return False

    if str(rule.get("event_id")).strip() != event_id:
        return False

    norm_img = normalize_path(image)
    target_img = normalize_path(rule.get("image", ""))

    # Match if normalized full path equals target or basenames match
    if norm_img == target_img:
        return True
    if os.path.basename(norm_img) == os.path.basename(target_img):
        return True
    return False


def make_non_overwriting_filename(input_path: str, suffix: str = "_labeled") -> str:
    base, ext = os.path.splitext(input_path)
    candidate = base + suffix + ext
    i = 1
    while os.path.exists(candidate) or os.path.abspath(candidate) == os.path.abspath(input_path):
        candidate = f"{base}{suffix}_{i}{ext}"
        i += 1
    return candidate


def main():
    p = argparse.ArgumentParser(description="Label logs by hardcoded (event_id, Image) rules")
    p.add_argument("filename", help="Path to input JSON file (list of logs or dict with 'logs')")
    p.add_argument("--dry-run", action="store_true", help="Do not write output; just report how many would be changed")
    p.add_argument("--out", help="Output filename (default: <input>_labeled.json or similar, chosen to avoid overwrite)")
    args = p.parse_args()

    if not os.path.exists(args.filename):
        print(f"File not found: {args.filename}")
        sys.exit(1)

    data = load_json_file(args.filename)

    if isinstance(data, dict) and "logs" in data and isinstance(data["logs"], list):
        logs = data["logs"]
        container_type = "dict"
    elif isinstance(data, list):
        logs = data
        container_type = "list"
    else:
        print("No logs list found in the provided JSON file.")
        sys.exit(1)

    # Pre-normalize rule images
    normalized_rules = []
    for r in FILTER_RULES:
        rr = deepcopy(r)
        rr["image_norm"] = normalize_path(rr.get("image", ""))
        rr["event_id"] = str(rr.get("event_id", "")).strip()
        normalized_rules.append(rr)

    total = len(logs)
    modified = 0
    per_rule_counts = {i: 0 for i in range(len(normalized_rules))}

    # Work on a deep copy to avoid in-memory mutation of original object
    out_logs = deepcopy(logs)

    for idx, item in enumerate(out_logs):
        for i, rule in enumerate(normalized_rules):
            if matches_rule(item, rule):
                # Apply the label and mitre_techniques
                prev_label = item.get("label")
                prev_mitre = item.get("mitre_techniques")
                item["label"] = rule.get("label")
                item["mitre_techniques"] = deepcopy(rule.get("mitre_techniques", []))
                per_rule_counts[i] += 1
                modified += 1
                # Do not apply multiple rules multiple times to same item
                break

    print(f"Processed {total} logs; {modified} logs matched and were relabeled.")
    for i, cnt in per_rule_counts.items():
        if cnt:
            print(f"  Rule {i}: matched {cnt} logs -> label '{normalized_rules[i]['label']}'")

    if args.dry_run:
        print("Dry run enabled — no file written.")
        sys.exit(0)

    # Prepare output structure and ensure we don't overwrite the input
    if container_type == "dict":
        out_data = deepcopy(data)
        out_data["logs"] = out_logs
    else:
        out_data = out_logs

    if args.out:
        out_filename = args.out
        if os.path.abspath(out_filename) == os.path.abspath(args.filename):
            out_filename = make_non_overwriting_filename(args.filename)
            print(f"Provided output filename equals input; will write to {out_filename} instead to avoid overwriting the original.")
        elif os.path.exists(out_filename):
            out_filename = make_non_overwriting_filename(out_filename, suffix="_labeled")
            print(f"Provided output file exists; writing to {out_filename} instead to avoid overwriting.")
    else:
        out_filename = make_non_overwriting_filename(args.filename)

    with open(out_filename, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"Wrote relabeled file to {out_filename}. Original file left intact.")


if __name__ == "__main__":
    main()
