#!/usr/bin/env python3
"""
Mapper: Revenue by Pickup Location.
Key = PULocationID -> Value = fare_amount,tip_amount,total_amount,trip_distance,1
"""
import sys, csv
reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        pu = row[7]
        fare, tip, total, dist = row[10], row[13], row[16], row[4]
        print(f"{pu}\t{fare},{tip},{total},{dist},1")
    except IndexError:
        continue
