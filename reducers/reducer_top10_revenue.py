#!/usr/bin/env python3
"""
Reducer - STAGE 2. Receives all (zone, total_revenue) pairs under the single key "ALL",
sorts them, and prints the Top 10 highest-revenue pickup zones.
"""
import sys
records = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, value = line.split("\t")
    zone, total_revenue = value.split(",")
    records.append((zone, float(total_revenue)))

records.sort(key=lambda x: -x[1])
for rank, (zone, revenue) in enumerate(records[:10], start=1):
    print(f"{rank}\t{zone}\t{revenue:.2f}")
