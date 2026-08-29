#!/usr/bin/env python3
"""Reducer: sums trip counts per pickup zone; also prints Top10/Bottom10 to stderr for the log."""
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

ranked = sorted(totals.items(), key=lambda x: -x[1])
sys.stderr.write("TOP10:" + str(ranked[:10]) + "\n")
sys.stderr.write("BOTTOM10:" + str(ranked[-10:]) + "\n")
