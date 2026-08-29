#!/usr/bin/env python3
"""Mapper: Trip Duration Analysis. Bucket trip_duration_min into categories."""
import sys, csv

def bucket(m):
    m = float(m)
    if m <= 5: return "0-5min"
    if m <= 15: return "5-15min"
    if m <= 30: return "15-30min"
    if m <= 60: return "30-60min"
    return "60+min"

reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        dur, fare, dist, tip = row[20], row[10], row[4], row[13]
        cat = bucket(dur)
        print(f"{cat}\t{fare},{dist},{tip},1")
    except (IndexError, ValueError):
        continue
