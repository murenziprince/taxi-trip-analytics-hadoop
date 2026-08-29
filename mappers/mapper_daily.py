#!/usr/bin/env python3
"""Mapper: Daily Demand. Key = day_of_week|is_weekend -> 1"""
import sys, csv
reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        dow, is_weekend = row[23], row[24]
        print(f"{dow}|{is_weekend}\t1")
    except IndexError:
        continue
