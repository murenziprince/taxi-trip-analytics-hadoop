#!/usr/bin/env python3
"""Reducer: aggregates trips, revenue, avg fare, avg tip per payment_type."""
import sys
PAYMENT_LABELS = {"0":"Flex Fare/Unspecified","1":"Credit Card","2":"Cash","3":"No Charge","4":"Dispute","5":"Unknown","6":"Voided Trip"}

current_key = None
n, sum_total, sum_tip = 0, 0.0, 0.0

def flush(key):
    if key is not None and n > 0:
        label = PAYMENT_LABELS.get(key, key)
        print(f"{key}\t{label},{n},{sum_total:.2f},{sum_total/n:.2f},{sum_tip/n:.2f}")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, value = line.split("\t")
    total, tip, cnt = value.split(",")
    if key != current_key:
        flush(current_key)
        current_key = key
        n, sum_total, sum_tip = 0, 0.0, 0.0
    n += int(cnt)
    sum_total += float(total)
    sum_tip += float(tip)
flush(current_key)
