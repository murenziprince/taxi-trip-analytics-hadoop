#!/usr/bin/env python3
"""Mapper: Distance-Based Fare Analysis. Bucket trip_distance into categories."""
import sys, csv

def bucket(d):
    d = float(d)
    if d <= 2: return "0-2mi"
    if d <= 5: return "2-5mi"
    if d <= 10: return "5-10mi"
    if d <= 20: return "10-20mi"
    return "20+mi"

reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        dist, fare, total = row[4], row[10], row[16]
        cat = bucket(dist)
        print(f"{cat}\t{fare},{total},{dist},1")
    except (IndexError, ValueError):
        continue
