#!/usr/bin/env python3
"""Mapper: Busiest Pickup-Dropoff Routes. Key = PULocationID->DOLocationID"""
import sys, csv
reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        pu, do, total = row[7], row[8], row[16]
        print(f"{pu}->{do}\t{total},1")
    except IndexError:
        continue
