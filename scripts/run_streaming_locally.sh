#!/bin/bash
# run_streaming_locally.sh
# ---------------------------------------------------------------------------
# Locally emulates Hadoop Streaming's execution contract for each job:
#     cat <input> | mapper.py | sort | reducer.py > <output>/part-00000
# This is *exactly* what Hadoop Streaming does per-partition (map -> shuffle&sort
# by key -> reduce). It validates mapper/reducer logic and produces real output
# before running the identical, unmodified scripts on an actual cluster via:
#     hadoop jar hadoop-streaming-*.jar -input ... -output ... -mapper ... -reducer ...
# See commands.txt for the real cluster invocation of each job.
# ---------------------------------------------------------------------------
set -e
cd /home/claude/taxi_project
IN=input/cleaned/yellow_tripdata_2026-01_cleaned.csv
LOG=report_assets/local_run_log.txt
> "$LOG"

run_job () {
  NAME=$1; MAPPER=$2; REDUCER=$3; OUT=$4; SRC=${5:-$IN}
  echo "=== JOB: $NAME ===" | tee -a "$LOG"
  START=$(date +%s.%N)
  cat "$SRC" | python3 "$MAPPER" | sort | python3 "$REDUCER" > "$OUT/part-00000" 2> "$OUT/stderr_log.txt"
  END=$(date +%s.%N)
  ELAPSED=$(echo "$END - $START" | bc)
  LINES=$(wc -l < "$OUT/part-00000")
  echo "  output rows: $LINES | elapsed: ${ELAPSED}s" | tee -a "$LOG"
  echo "$NAME,$ELAPSED,$LINES" >> report_assets/timing.csv
}

echo "job,elapsed_sec,output_rows" > report_assets/timing.csv

run_job "hourly"   mappers/mapper_hourly.py   reducers/reducer_hourly.py   output/hourly
run_job "daily"    mappers/mapper_daily.py    reducers/reducer_daily.py    output/daily
run_job "location" mappers/mapper_location.py reducers/reducer_location.py output/locations
run_job "revenue"  mappers/mapper_revenue.py  reducers/reducer_revenue.py  output/revenue
run_job "payment"  mappers/mapper_payment.py  reducers/reducer_payment.py  output/payment
run_job "distance" mappers/mapper_distance.py reducers/reducer_distance.py output/distance
run_job "route"    mappers/mapper_route.py    reducers/reducer_route.py    output/routes
run_job "duration" mappers/mapper_duration.py reducers/reducer_duration.py output/duration
run_job "anomaly"  mappers/mapper_anomaly.py  reducers/reducer_anomaly.py  output/anomalies

# ---- Multi-stage job: Stage 2 consumes Stage 1 (revenue) output ----
echo "=== JOB: revenue_top10 (multi-stage, Stage 2) ===" | tee -a "$LOG"
START=$(date +%s.%N)
cat output/revenue/part-00000 | python3 mappers/mapper_top10_revenue.py | sort | python3 reducers/reducer_top10_revenue.py > output/revenue_top10/part-00000
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
echo "  elapsed: ${ELAPSED}s" | tee -a "$LOG"
echo "revenue_top10,$ELAPSED,$(wc -l < output/revenue_top10/part-00000)" >> report_assets/timing.csv

echo "ALL JOBS COMPLETE" | tee -a "$LOG"
cat report_assets/timing.csv
