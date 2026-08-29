#!/usr/bin/env python3
"""Mapper: Payment Method Analysis. Key = payment_type -> total_amount,tip_amount,1"""
import sys, csv
reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        ptype, total, tip = row[9], row[16], row[13]
        print(f"{ptype}\t{total},{tip},1")
    except IndexError:
        continue
