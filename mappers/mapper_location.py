#!/usr/bin/env python3
"""Mapper: Pickup Location Analysis. Key = PULocationID -> 1"""
import sys, csv
reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        print(f"{row[7]}\t1")   # PULocationID
    except IndexError:
        continue
