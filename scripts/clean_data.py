"""
clean_data.py - multi-month version
Converts and cleans all 2 months of TLC Yellow Taxi data, combining them
into a single cleaned CSV used as input for every MapReduce job.
"""
import pandas as pd
import json, os

DOWNLOADS = r"C:\Users\prizz\Downloads"
PARQUET_FILES = [
    os.path.join(DOWNLOADS, "yellow_tripdata_2026-01.parquet"),
    os.path.join(DOWNLOADS, "yellow_tripdata_2026-02.parquet"),
    
]
PROJECT = r"C:\taxi_project_assignment1"
RAW_CSV = os.path.join(PROJECT, "input", "raw", "yellow_tripdata_2026_JanFeb.csv")
CLEANED_CSV = os.path.join(PROJECT, "input", "cleaned", "yellow_tripdata_2026_Q1_cleaned.csv")
AUDIT_JSON = os.path.join(PROJECT, "report_assets", "cleaning_audit.json")

os.makedirs(os.path.join(PROJECT, "input", "raw"), exist_ok=True)
os.makedirs(os.path.join(PROJECT, "input", "cleaned"), exist_ok=True)
os.makedirs(os.path.join(PROJECT, "report_assets"), exist_ok=True)

audit = {"stage": "data_cleaning", "rules": [], "months_included": [os.path.basename(f) for f in PARQUET_FILES]}

def log_rule(name, description, n_affected, total):
    pct = round(100 * n_affected / total, 4) if total else 0
    audit["rules"].append({"rule": name, "description": description,
                            "records_affected": int(n_affected), "pct_of_dataset": pct})
    print(f"[{name}] {description} -> {n_affected:,} records ({pct}%)")

# ---- Load and combine all months ----
dfs = []
for fp in PARQUET_FILES:
    print(f"Loading {fp} ...")
    dfs.append(pd.read_parquet(fp))
df = pd.concat(dfs, ignore_index=True)
total_raw = len(df)
audit["total_raw_records"] = int(total_raw)
print(f"Combined raw records across {len(PARQUET_FILES)} months: {total_raw:,}")

df.to_csv(RAW_CSV, index=False)
print(f"Wrote raw CSV: {RAW_CSV} ({os.path.getsize(RAW_CSV)/1e6:.1f} MB)")

# ---- Cleaning rules (same logic as before) ----
dupe_mask = df.duplicated(keep="first")
log_rule("duplicates", "Exact duplicate rows (kept first occurrence)", dupe_mask.sum(), total_raw)
df = df[~dupe_mask].copy()

bad_time_order = df["tpep_dropoff_datetime"] <= df["tpep_pickup_datetime"]
log_rule("invalid_timestamp_order", "Dropoff time <= pickup time", bad_time_order.sum(), total_raw)
df = df[~bad_time_order].copy()

duration_min = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60.0
df["trip_duration_min"] = duration_min
bad_duration = (duration_min <= 0) | (duration_min > 24 * 60)
log_rule("impossible_duration", "Trip duration <= 0 min or > 1440 min (24h)", bad_duration.sum(), total_raw)
df = df[~bad_duration].copy()

bad_distance = df["trip_distance"] <= 0
log_rule("zero_negative_distance", "trip_distance <= 0 miles", bad_distance.sum(), total_raw)
df = df[~bad_distance].copy()

extreme_distance = df["trip_distance"] > 100
log_rule("extreme_distance", "trip_distance > 100 miles", extreme_distance.sum(), total_raw)
df = df[~extreme_distance].copy()

missing_passengers = df["passenger_count"].isna()
log_rule("missing_passenger_count_imputed", "Missing passenger_count imputed to 1", missing_passengers.sum(), total_raw)
df["passenger_count"] = df["passenger_count"].fillna(1)

bad_passengers = (df["passenger_count"] <= 0) | (df["passenger_count"] > 6)
log_rule("invalid_passenger_count", "Reported passenger_count <=0 or >6", bad_passengers.sum(), total_raw)
df = df[~bad_passengers].copy()

bad_fare = (df["fare_amount"] <= 0) | (df["total_amount"] <= 0)
log_rule("invalid_fare", "fare_amount <= 0 or total_amount <= 0", bad_fare.sum(), total_raw)
df = df[~bad_fare].copy()

extreme_fare = df["total_amount"] > 1000
log_rule("extreme_fare", "total_amount > $1000", extreme_fare.sum(), total_raw)
df = df[~extreme_fare].copy()

bad_location = (~df["PULocationID"].between(1, 263)) | (~df["DOLocationID"].between(1, 263))
log_rule("invalid_location_id", "PU/DOLocationID outside valid TLC zone range 1-263", bad_location.sum(), total_raw)
df = df[~bad_location].copy()

for col, default, label in [("RatecodeID", 1, "RatecodeID imputed to 1"),
                              ("store_and_fwd_flag", "N", "store_and_fwd_flag imputed to N")]:
    n_missing = df[col].isna().sum()
    log_rule(f"missing_{col}_imputed", label, n_missing, total_raw)
    df[col] = df[col].fillna(default)
df["RatecodeID"] = df["RatecodeID"].astype(int)

for col in ["congestion_surcharge", "Airport_fee"]:
    n_missing = df[col].isna().sum()
    log_rule(f"missing_{col}_imputed", f"Missing {col} imputed to 0.0", n_missing, total_raw)
    df[col] = df[col].fillna(0.0)

fee_cols = ["extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge",
            "congestion_surcharge", "Airport_fee", "cbd_congestion_fee"]
neg_fee_rows = (df[fee_cols] < 0).any(axis=1)
log_rule("negative_fee_components", "Negative fee component(s) clipped to 0", neg_fee_rows.sum(), total_raw)
for col in fee_cols:
    df[col] = df[col].clip(lower=0)

df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
df["pickup_date"] = df["tpep_pickup_datetime"].dt.date.astype(str)
df["pickup_dow"] = df["tpep_pickup_datetime"].dt.day_name()
df["is_weekend"] = df["tpep_pickup_datetime"].dt.dayofweek >= 5

total_clean = len(df)
audit["total_clean_records"] = int(total_clean)
audit["total_removed"] = int(total_raw - total_clean)
audit["pct_removed"] = round(100 * (total_raw - total_clean) / total_raw, 4)

df.to_csv(CLEANED_CSV, index=False)
with open(AUDIT_JSON, "w") as f:
    json.dump(audit, f, indent=2)

print(f"\nRaw records:   {total_raw:,}")
print(f"Clean records: {total_clean:,}")
print(f"Removed:       {total_raw - total_clean:,} ({audit['pct_removed']}%)")
print(f"Wrote cleaned CSV: {CLEANED_CSV} ({os.path.getsize(CLEANED_CSV)/1e6:.1f} MB)")