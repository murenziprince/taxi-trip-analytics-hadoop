#!/usr/bin/env python3
"""
Mapper - STAGE 2 of the multi-stage job.
Consumes the HDFS output of Job 1 (revenue by pickup zone: output/revenue/part-*)
Re-keys every record to a single constant key "ALL" so that every zone's revenue
total lands on ONE reducer, which can then sort globally and emit the Top 10.
This is the standard 'funnel everything to one reducer' pattern for global top-N.
"""
import sys
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    zone, stats = line.split("\t")
    n, sum_fare, sum_tip, sum_total, avg_fare, avg_dist = stats.split(",")
    print(f"ALL\t{zone},{sum_total}")
