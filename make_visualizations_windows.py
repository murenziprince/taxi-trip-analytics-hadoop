"""
make_visualizations.py (Windows / real-cluster-output version)
Reads the part-00000 files you pulled from HDFS (final_outputs\\*.tsv)
and generates the 7 required charts.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import os

PROJECT = r"C:\taxi_project_assignment1"
IN = os.path.join(PROJECT, "final_outputs")
OUT = os.path.join(PROJECT, "report_assets")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "font.size": 10})

# ---- 1. Trips by hour ----
hourly = pd.read_csv(os.path.join(IN, "hourly.tsv"), sep="\t", header=None, names=["hour", "trips"])
hourly["hour"] = hourly["hour"].astype(int)
hourly = hourly.sort_values("hour")
plt.figure(figsize=(9, 4.5))
plt.bar(hourly["hour"], hourly["trips"], color="#2563eb")
plt.xlabel("Hour of Day"); plt.ylabel("Trip Count"); plt.title("Taxi Trips by Hour of Day")
plt.xticks(range(0, 24))
plt.tight_layout(); plt.savefig(os.path.join(OUT, "01_trips_by_hour.png")); plt.close()
busiest_hour = hourly.loc[hourly["trips"].idxmax()]
quietest_hour = hourly.loc[hourly["trips"].idxmin()]

# ---- 2. Trips by day of week ----
daily = pd.read_csv(os.path.join(IN, "daily.tsv"), sep="\t", header=None, names=["day", "trips"])
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily["day"] = pd.Categorical(daily["day"], categories=order, ordered=True)
daily = daily.sort_values("day")
colors = ["#2563eb"] * 5 + ["#f59e0b"] * 2
plt.figure(figsize=(8, 4.5))
plt.bar(daily["day"], daily["trips"], color=colors)
plt.ylabel("Trip Count"); plt.title("Taxi Trips by Day of Week (blue=weekday, orange=weekend)")
plt.xticks(rotation=30); plt.tight_layout(); plt.savefig(os.path.join(OUT, "02_trips_by_day.png")); plt.close()
busiest_day = daily.loc[daily["trips"].idxmax()]

# ---- 3. Top 10 pickup zones ----
loc = pd.read_csv(os.path.join(IN, "locations.tsv"), sep="\t", header=None, names=["zone", "trips"])
top10loc = loc.sort_values("trips", ascending=False).head(10)
bottom10loc = loc.sort_values("trips", ascending=True).head(10)
plt.figure(figsize=(8, 4.5))
plt.barh([f"Zone {z}" for z in top10loc["zone"]][::-1], top10loc["trips"][::-1], color="#059669")
plt.xlabel("Trip Count"); plt.title("Top 10 Pickup Zones by Trip Count")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "03_top10_pickup_zones.png")); plt.close()

# ---- 4. Revenue by payment method ----
PAYMENT_LABELS = {0:"Flex Fare/Unspecified",1:"Credit Card",2:"Cash",3:"No Charge",4:"Dispute",5:"Unknown",6:"Voided Trip"}
pay = pd.read_csv(os.path.join(IN, "payment.tsv"), sep="\t", header=None, names=["code", "stats"])
pay[["label", "trips", "total_revenue", "avg_fare", "avg_tip"]] = pay["stats"].str.split(",", expand=True)
pay["total_revenue"] = pay["total_revenue"].astype(float)
pay = pay.sort_values("total_revenue", ascending=False)
plt.figure(figsize=(7, 4.5))
plt.bar(pay["label"], pay["total_revenue"] / 1e6, color="#7c3aed")
plt.ylabel("Total Revenue ($ Millions)"); plt.title("Total Revenue by Payment Method")
plt.xticks(rotation=20); plt.tight_layout(); plt.savefig(os.path.join(OUT, "04_revenue_by_payment.png")); plt.close()

# ---- 5. Trips by distance category ----
dist = pd.read_csv(os.path.join(IN, "distance.tsv"), sep="\t", header=None, names=["category", "stats"])
dist[["trips", "avg_fare", "avg_total", "avg_dist"]] = dist["stats"].str.split(",", expand=True)
dist["trips"] = dist["trips"].astype(int)
cat_order = ["0-2mi", "2-5mi", "5-10mi", "10-20mi", "20+mi"]
dist["category"] = pd.Categorical(dist["category"], categories=cat_order, ordered=True)
dist = dist.sort_values("category")
plt.figure(figsize=(7, 4.5))
plt.bar(dist["category"], dist["trips"], color="#dc2626")
plt.ylabel("Trip Count"); plt.title("Trips by Distance Category")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "05_trips_by_distance_category.png")); plt.close()

# ---- 6. Top 10 routes ----
routes = pd.read_csv(os.path.join(IN, "routes.tsv"), sep="\t", header=None, names=["route", "stats"])
routes[["trips", "revenue"]] = routes["stats"].str.split(",", expand=True)
routes["trips"] = routes["trips"].astype(int)
routes["revenue"] = routes["revenue"].astype(float)
top10routes_count = routes.sort_values("trips", ascending=False).head(10)
top10routes_rev = routes.sort_values("revenue", ascending=False).head(10)
plt.figure(figsize=(8, 4.5))
plt.barh(top10routes_count["route"][::-1], top10routes_count["trips"][::-1], color="#0891b2")
plt.xlabel("Trip Count"); plt.title("Top 10 Routes by Trip Count")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "06_top10_routes.png")); plt.close()

# ---- 7. Revenue vs distance ----
plt.figure(figsize=(7, 4.5))
plt.plot(dist["category"], dist["avg_total"].astype(float), marker="o", color="#ea580c", linewidth=2)
plt.ylabel("Average Total Fare ($)"); plt.title("Average Revenue vs Distance Category")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "07_revenue_vs_distance.png")); plt.close()

# ---- Print key numbers you'll need for the report text ----
print("=" * 60)
print("KEY NUMBERS FOR YOUR REPORT")
print("=" * 60)
print(f"Busiest hour: {int(busiest_hour['hour'])}:00 ({int(busiest_hour['trips']):,} trips)")
print(f"Quietest hour: {int(quietest_hour['hour'])}:00 ({int(quietest_hour['trips']):,} trips)")
print(f"Busiest day: {busiest_day['day']} ({int(busiest_day['trips']):,} trips)")
print(f"Top pickup zone: {int(top10loc.iloc[0]['zone'])} ({int(top10loc.iloc[0]['trips']):,} trips)")
print(f"Top 10 zones by trips: {list(zip(top10loc['zone'].astype(int), top10loc['trips'].astype(int)))}")
print(f"Bottom 10 zones by trips: {list(zip(bottom10loc['zone'].astype(int), bottom10loc['trips'].astype(int)))}")
print(f"Top payment method by revenue: {pay.iloc[0]['label']} (${pay.iloc[0]['total_revenue']:,.2f})")
print(f"Highest avg fare distance category: {dist.loc[dist['avg_total'].astype(float).idxmax(), 'category']}")
print(f"Most frequent route: {top10routes_count.iloc[0]['route']} ({int(top10routes_count.iloc[0]['trips']):,} trips)")
print(f"Most profitable route: {top10routes_rev.iloc[0]['route']} (${top10routes_rev.iloc[0]['revenue']:,.2f})")
print("Top 10 revenue zones (from revenue_top10.tsv) - see that file directly")
print("=" * 60)
print(f"\nAll 7 charts saved to {OUT}")
