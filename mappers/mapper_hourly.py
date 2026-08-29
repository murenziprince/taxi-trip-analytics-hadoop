#!/usr/bin/env python3
"""
Mapper: Hourly Taxi Demand
Key-Value design: emit (pickup_hour) -> 1  for every trip.
The Reducer sums the 1s per hour (classic word-count pattern).
"""
import sys, csv

reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":   # skip header / blank lines
        continue
    try:
        pickup_hour = row[21]             # pickup_hour column
        print(f"{pickup_hour}\t1")
    except IndexError:
        continue
