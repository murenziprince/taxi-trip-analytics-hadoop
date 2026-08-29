#!/usr/bin/env python3
"""Reducer: sums trip count & revenue per route, prints Top20-by-count and Top20-by-revenue to stderr."""
import sys
current_key = None
n, sum_total = 0, 0.0
by_count, by_revenue = {}, {}

def flush(key):
    if key is not None and n > 0:
        print(f"{key}\t{n},{sum_total:.2f}")
        by_count[key] = n
        by_revenue[key] = sum_total

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, value = line.split("\t")
    total, cnt = value.split(",")
    if key != current_key:
        flush(current_key)
        current_key = key
        n, sum_total = 0, 0.0
    n += int(cnt)
    sum_total += float(total)
flush(current_key)

top20_count = sorted(by_count.items(), key=lambda x: -x[1])[:20]
top20_rev = sorted(by_revenue.items(), key=lambda x: -x[1])[:20]
sys.stderr.write("TOP20_BY_COUNT:" + str(top20_count) + "\n")
sys.stderr.write("TOP20_BY_REVENUE:" + str(top20_rev) + "\n")
