import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import ast

BASE = "/home/claude/taxi_project"
OUT = f"{BASE}/report_assets"
plt.rcParams.update({"figure.dpi": 130, "font.size": 10})

# ---- 1. Trips by hour ----
hourly = pd.read_csv(f"{BASE}/output/hourly/part-00000", sep="\t", header=None, names=["hour", "trips"])
hourly["hour"] = hourly["hour"].astype(int)
hourly = hourly.sort_values("hour")
plt.figure(figsize=(9, 4.5))
plt.bar(hourly["hour"], hourly["trips"], color="#2563eb")
plt.xlabel("Hour of Day"); plt.ylabel("Trip Count"); plt.title("Taxi Trips by Hour of Day (Jan 2026)")
plt.xticks(range(0, 24))
plt.tight_layout(); plt.savefig(f"{OUT}/01_trips_by_hour.png"); plt.close()

# ---- 2. Trips by day of week ----
daily = pd.read_csv(f"{BASE}/output/daily/part-00000", sep="\t", header=None, names=["day", "trips"])
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily["day"] = pd.Categorical(daily["day"], categories=order, ordered=True)
daily = daily.sort_values("day")
colors = ["#2563eb"] * 5 + ["#f59e0b"] * 2
plt.figure(figsize=(8, 4.5))
plt.bar(daily["day"], daily["trips"], color=colors)
plt.ylabel("Trip Count"); plt.title("Taxi Trips by Day of Week (blue=weekday, orange=weekend)")
plt.xticks(rotation=30); plt.tight_layout(); plt.savefig(f"{OUT}/02_trips_by_day.png"); plt.close()

# ---- 3. Top 10 pickup zones ----
with open(f"{BASE}/output/locations/stderr_log.txt") as f:
    for line in f:
        if line.startswith("TOP10:"):
            top10 = ast.literal_eval(line.replace("TOP10:", "").strip())
zones, counts = zip(*top10)
plt.figure(figsize=(8, 4.5))
plt.barh([f"Zone {z}" for z in zones][::-1], counts[::-1], color="#059669")
plt.xlabel("Trip Count"); plt.title("Top 10 Pickup Zones by Trip Count")
plt.tight_layout(); plt.savefig(f"{OUT}/03_top10_pickup_zones.png"); plt.close()

# ---- 4. Revenue by payment method ----
pay = pd.read_csv(f"{BASE}/output/payment/part-00000", sep="\t", header=None,
                   names=["code", "stats"])
pay[["label", "trips", "total_revenue", "avg_fare", "avg_tip"]] = pay["stats"].str.split(",", expand=True)
pay["total_revenue"] = pay["total_revenue"].astype(float)
pay = pay.sort_values("total_revenue", ascending=False)
plt.figure(figsize=(7, 4.5))
plt.bar(pay["label"], pay["total_revenue"] / 1e6, color="#7c3aed")
plt.ylabel("Total Revenue ($ Millions)"); plt.title("Total Revenue by Payment Method")
plt.xticks(rotation=20); plt.tight_layout(); plt.savefig(f"{OUT}/04_revenue_by_payment.png"); plt.close()

# ---- 5. Trips by distance category ----
dist = pd.read_csv(f"{BASE}/output/distance/part-00000", sep="\t", header=None,
                    names=["category", "stats"])
dist[["trips", "avg_fare", "avg_total", "avg_dist"]] = dist["stats"].str.split(",", expand=True)
dist["trips"] = dist["trips"].astype(int)
cat_order = ["0-2mi", "2-5mi", "5-10mi", "10-20mi", "20+mi"]
dist["category"] = pd.Categorical(dist["category"], categories=cat_order, ordered=True)
dist = dist.sort_values("category")
plt.figure(figsize=(7, 4.5))
plt.bar(dist["category"], dist["trips"], color="#dc2626")
plt.ylabel("Trip Count"); plt.title("Trips by Distance Category")
plt.tight_layout(); plt.savefig(f"{OUT}/05_trips_by_distance_category.png"); plt.close()

# ---- 6. Top 10 routes (by count, from stderr log) ----
with open(f"{BASE}/output/routes/stderr_log.txt") as f:
    for line in f:
        if line.startswith("TOP20_BY_COUNT:"):
            top20 = ast.literal_eval(line.replace("TOP20_BY_COUNT:", "").strip())
top10routes = top20[:10]
routes, rcounts = zip(*top10routes)
plt.figure(figsize=(8, 4.5))
plt.barh(routes[::-1], rcounts[::-1], color="#0891b2")
plt.xlabel("Trip Count"); plt.title("Top 10 Pickup->Dropoff Routes by Trip Count")
plt.tight_layout(); plt.savefig(f"{OUT}/06_top10_routes.png"); plt.close()

# ---- 7. Revenue vs distance (avg total fare per distance category) ----
plt.figure(figsize=(7, 4.5))
plt.plot(dist["category"], dist["avg_total"].astype(float), marker="o", color="#ea580c", linewidth=2)
plt.ylabel("Average Total Fare ($)"); plt.title("Average Revenue vs Distance Category")
plt.tight_layout(); plt.savefig(f"{OUT}/07_revenue_vs_distance.png"); plt.close()

print("All 7 visualizations saved to", OUT)
