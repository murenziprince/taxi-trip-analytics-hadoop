#!/usr/bin/env python3
"""
Mapper: Anomaly Detection (runs on the CLEANED data - looking for records that
are technically valid but statistically suspicious: extreme fare-per-mile,
very short/long durations relative to distance, mismatched fare vs distance, etc.)
Key = anomaly_type -> 1  (plus writes the full flagged record to stderr audit trail
in a real cluster this would go to a separate 'flagged records' output path).
"""
import sys, csv

reader = csv.reader(sys.stdin)
for row in reader:
    if not row or row[0] == "VendorID":
        continue
    try:
        dist = float(row[4])
        fare = float(row[10])
        total = float(row[16])
        dur = float(row[20])
        passengers = float(row[3])

        fare_per_mile = fare / dist if dist > 0 else 0
        speed_mph = (dist / (dur / 60.0)) if dur > 0 else 0

        # Each record gets exactly ONE category (priority order below) so that
        # counts across categories sum to the total record count with no double-counting.
        if fare_per_mile > 50:
            category = "extreme_fare_per_mile"
        elif speed_mph > 80:
            category = "implausible_speed"
        elif dur < 1 and dist > 1:
            category = "too_fast_for_duration"
        elif dist > 0 and fare == 0:
            category = "zero_fare_nonzero_distance"
        elif passengers > 6:
            category = "overcapacity_passengers"
        elif total < fare:
            category = "total_less_than_fare"
        else:
            category = "normal"

        print(f"{category}\t1")
    except (IndexError, ValueError, ZeroDivisionError):
        print("unparseable\t1")
