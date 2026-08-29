#!/usr/bin/env python3
"""Reducer: Daily Demand. Sums trips per day-of-week, then compares weekday vs weekend totals."""
import sys
current_key, current_count = None, 0
weekday_total, weekend_total = 0, 0
results = {}

def flush(key, count):
    global weekday_total, weekend_total
    if key is not None:
        day, is_weekend = key.split("|")
        print(f"{day}\t{count}")
        results[day] = count
        if is_weekend == "True":
            weekend_total += count
        else:
            weekday_total += count

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, value = line.split("\t")
    if key == current_key:
        current_count += int(value)
    else:
        flush(current_key, current_count)
        current_key, current_count = key, int(value)
flush(current_key, current_count)

sys.stderr.write(f"WEEKDAY_TOTAL\t{weekday_total}\n")
sys.stderr.write(f"WEEKEND_TOTAL\t{weekend_total}\n")
if results:
    busiest_day = max(results, key=results.get)
    sys.stderr.write(f"BUSIEST_DAY\t{busiest_day}\t{results[busiest_day]}\n")
