#!/usr/bin/env python3
"""Reducer: counts records per anomaly type, prints % of dataset flagged to stderr."""
import sys
current_key, current_count = None, 0
totals = {}

def flush(key, count):
    if key is not None:
        print(f"{key}\t{count}")
        totals[key] = count

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, value = line.split("\t")
    if key == current_key:
        current_count += int(value)
    else:
        flush(current_key, current_count)
        current_key, current_count = key, int(value)
flush(current_key, current_count)

total_records = sum(totals.values())
flagged = total_records - totals.get("normal", 0)
pct = 100 * flagged / total_records if total_records else 0
sys.stderr.write(f"TOTAL_RECORDS\t{total_records}\n")
sys.stderr.write(f"TOTAL_FLAGGED\t{flagged}\n")
sys.stderr.write(f"PCT_FLAGGED\t{pct:.2f}%\n")
