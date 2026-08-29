#!/usr/bin/env python3
"""Reducer: avg fare, avg distance, avg tip, trip count per duration category."""
import sys
current_key = None
n, sum_fare, sum_dist, sum_tip = 0, 0.0, 0.0, 0.0

def flush(key):
    if key is not None and n > 0:
        print(f"{key}\t{n},{sum_fare/n:.2f},{sum_dist/n:.2f},{sum_tip/n:.2f}")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, value = line.split("\t")
    fare, dist, tip, cnt = value.split(",")
    if key != current_key:
        flush(current_key)
        current_key = key
        n, sum_fare, sum_dist, sum_tip = 0, 0.0, 0.0, 0.0
    n += int(cnt)
    sum_fare += float(fare)
    sum_dist += float(dist)
    sum_tip += float(tip)
flush(current_key)
