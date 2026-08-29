"""
performance_comparison.py (Windows-safe version)
Runs the SAME analysis (revenue by pickup zone) two ways and records time:
  1. Ordinary single-machine Pandas
  2. The Hadoop-Streaming-equivalent Mapper -> Sort -> Reducer pipeline
"""
import subprocess, time, os, json
import pandas as pd

PROJECT = r"C:\taxi_project_assignment1"
CSV = os.path.join(PROJECT, "input", "cleaned", "yellow_tripdata_2026_Q1_cleaned.csv")
MAPPER = os.path.join(PROJECT, "mappers", "mapper_revenue.py")
REDUCER = os.path.join(PROJECT, "reducers", "reducer_revenue.py")
OUT_JSON = os.path.join(PROJECT, "report_assets", "performance_comparison.json")
TMP_OUT = os.path.join(PROJECT, "perf_test_out.txt")

os.makedirs(os.path.join(PROJECT, "report_assets"), exist_ok=True)

results = {}

# ---- Dataset facts ----
size_mb = os.path.getsize(CSV) / 1e6
n_records = sum(1 for _ in open(CSV, encoding="utf-8")) - 1
results["dataset_size_mb"] = round(size_mb, 1)
results["num_records"] = n_records

# ---- 1. Pandas ----
t0 = time.time()
df = pd.read_csv(CSV)
agg = df.groupby("PULocationID").agg(
    trip_count=("PULocationID", "size"),
    total_fare=("fare_amount", "sum"),
    total_tip=("tip_amount", "sum"),
    total_revenue=("total_amount", "sum"),
    avg_fare=("fare_amount", "mean"),
    avg_distance=("trip_distance", "mean"),
)
t1 = time.time()
results["pandas_time_sec"] = round(t1 - t0, 2)

try:
    import psutil
    results["pandas_peak_mem_mb"] = round(psutil.Process(os.getpid()).memory_info().rss / 1e6, 1)
except ImportError:
    results["pandas_peak_mem_mb"] = "psutil not installed - run: pip install psutil"

del df, agg

# ---- 2. Streaming pipeline (Mapper | Sort | Reducer) ----
t0 = time.time()
cmd = f'type "{CSV}" | python "{MAPPER}" | sort | python "{REDUCER}" > "{TMP_OUT}"'
subprocess.run(cmd, shell=True, check=True)
t1 = time.time()
results["streaming_time_sec"] = round(t1 - t0, 2)
results["streaming_output_kb"] = round(os.path.getsize(TMP_OUT) / 1024, 1)

block_size_mb = 128
results["est_mapper_tasks_on_cluster"] = max(1, round(size_mb / block_size_mb))
results["est_reducer_tasks_on_cluster"] = 1

with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))