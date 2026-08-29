#!/usr/bin/env python3
"""
Reducer: Hourly Taxi Demand
Relies on Hadoop's Shuffle-and-Sort to group all values for the same hour together.
Sums counts per hour, then (since streaming reducers process one key at a time)
we also track running totals to print busiest/least-busy hour at the end.
"""
import sys

current_key = None
current_count = 0
all_totals = {}

def flush(key, count):
    if key is not None:
        print(f"{key}\t{count}")
        all_totals[key] = count

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, value = line.split("\t")
    if key == current_key:
        current_count += int(value)
    else:
        flush(current_key, current_count)
        current_key = key
        current_count = int(value)
flush(current_key, current_count)

if all_totals:
    busiest = max(all_totals, key=all_totals.get)
    quietest = min(all_totals, key=all_totals.get)
    sys.stderr.write(f"BUSIEST_HOUR\t{busiest}\t{all_totals[busiest]}\n")
    sys.stderr.write(f"QUIETEST_HOUR\t{quietest}\t{all_totals[quietest]}\n")
