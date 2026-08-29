import json
with open("report_assets/cleaning_audit.json") as f: cleaning = json.load(f)
with open("report_assets/performance_comparison.json") as f: perf = json.load(f)
print(json.dumps(cleaning, indent=2))
print(json.dumps(perf, indent=2))
