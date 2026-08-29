# Distributed Taxi Trip Analytics — Hadoop + HDFS + Python MapReduce

## What this is
Analyzes NYC TLC Yellow Taxi trip records (January 2026, ~3.72M raw records)
using the Hadoop Streaming Mapper/Reducer model. Includes data cleaning,
9 single-stage analyses (a-i from the brief), 1 multi-stage job (revenue by
zone -> top-10 revenue zones), a Pandas-vs-MapReduce performance comparison,
and required visualizations.

## Environment assumptions
- Hadoop 3.3.x with HDFS + YARN (single-node pseudo-distributed is sufficient)
- Python 3.8+ on every node (no third-party libraries needed for mappers/reducers
  — they use only `sys`, `csv` from the standard library, so no extra
  environment setup is needed on cluster worker nodes)
- Python 3 with `pandas` and `matplotlib` on the driver machine for
  `scripts/clean_data.py`, `scripts/performance_comparison.py`, and
  `scripts/make_visualizations.py`
- `JAVA_HOME`, `HADOOP_HOME` set; `hadoop`, `hdfs`, `yarn` on PATH

## Directory layout
```
taxi_project/
  input/raw/            raw CSV (mirrors HDFS /taxi_project/input/raw/)
  input/cleaned/         cleaned CSV (mirrors HDFS /taxi_project/input/cleaned/)
  mappers/                9 mapper scripts + 1 stage-2 mapper (top10 revenue)
  reducers/               9 reducer scripts + 1 stage-2 reducer
  output/<job>/           local job outputs (mirrors HDFS output paths)
  scripts/
    clean_data.py               parquet -> CSV, cleaning + audit log
    run_streaming_locally.sh    local cat|mapper|sort|reducer validation of every job
    performance_comparison.py   Pandas vs streaming-pipeline timing/memory
    make_visualizations.py      generates the 7 required charts
  report_assets/          cleaning_audit.json, timing.csv, performance_comparison.json, *.png
  commands.txt             every HDFS + Hadoop Streaming command to reproduce on a real cluster
```

## How to run
### 1. Local (no cluster needed) — validates all logic and produces real output/charts
```bash
python3 scripts/clean_data.py
bash scripts/run_streaming_locally.sh
python3 scripts/performance_comparison.py
python3 scripts/make_visualizations.py
```

### 2. On an actual Hadoop cluster
Follow `commands.txt` top to bottom: create the HDFS directory tree, `hdfs dfs -put`
the CSVs, then run each `hadoop jar hadoop-streaming-*.jar ...` command listed
there. The mapper/reducer `.py` files are identical to the ones validated
locally in step 1 — no code changes are needed between local validation and
cluster execution, which is the point of the Hadoop Streaming contract
(stdin/stdout line-oriented key\tvalue records).

## Design notes
- **Key-value design**: every mapper emits `key\tvalue` text lines on stdout.
  Reducers rely on Hadoop's Shuffle-and-Sort to receive all values for a key
  consecutively, so each reducer is written as a simple "detect key change,
  flush accumulated aggregate" streaming reducer (no need to buffer all data
  in memory — this is the actual scalability advantage of MapReduce).
- **Multi-stage job**: `output/revenue` (Stage 1: revenue per pickup zone) is
  consumed directly as the *input* to Stage 2 (`mapper_top10_revenue.py` /
  `reducer_top10_revenue.py`), which re-keys every zone to a single constant
  key so all 263 zone totals funnel to one reducer for a global Top-10 sort.
- **Anomaly categories are mutually exclusive** (checked in priority order) so
  that per-category counts sum exactly to total record count — avoids
  double-counting records with multiple issues.
