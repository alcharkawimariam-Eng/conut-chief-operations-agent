import pandas as pd
import numpy as np
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent  # .../conut-chief-operations-agent/data

input_path = BASE_DIR / "prepared data" / "cleaned_customer_orders.csv"
output_path = BASE_DIR / "prepared data" / "customer_orders_features.csv"

# ---------- 1) Load ----------
df = pd.read_csv(input_path)

# ---------- 2) Parse dates ----------
# Example format: 2025-12-30 19:30:
df["First_Order_dt"] = pd.to_datetime(
    df["First_Order"], format="%Y-%m-%d %H:%M:", errors="coerce"
)
df["Last_Order_dt"] = pd.to_datetime(
    df["Last_Order"], format="%Y-%m-%d %H:%M:", errors="coerce"
)

# ---------- 3) Basic customer features ----------
# Lifetime in days between first and last order
df["customer_lifetime_days"] = (
    df["Last_Order_dt"] - df["First_Order_dt"]
).dt.total_seconds() / 86400.0

# Average order value (handle divide by zero safely)
df["avg_order_value"] = np.where(
    df["Order_Count"] > 0,
    df["Total_Spent"] / df["Order_Count"],
    np.nan,
)

# One-time customer flag
df["is_one_time_customer"] = (df["Order_Count"] == 1).astype(int)

# ---------- 4) Recency & high-value flags ----------
# Recency: days since last order compared to most recent order in dataset
max_last_order = df["Last_Order_dt"].max()
df["recency_days"] = (
    max_last_order - df["Last_Order_dt"]
).dt.total_seconds() / 86400.0

# High-value customers: top 20% by Total_Spent
threshold_80 = df["Total_Spent"].quantile(0.80)
df["is_high_value_customer"] = (df["Total_Spent"] >= threshold_80).astype(int)

# ---------- 5) Quick check ----------
print(df.head())

# ---------- 6) Save ----------
df.to_csv(output_path, index=False)
print("Saved:", output_path)