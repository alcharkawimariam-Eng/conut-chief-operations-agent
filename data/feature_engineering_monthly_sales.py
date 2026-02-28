import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent

input_path = BASE_DIR / "prepared data" / "cleaned_monthly_branch_sales.csv"
output_path = BASE_DIR / "prepared data" / "monthly_branch_sales_features.csv"

# ---------- 1) Load ----------
df = pd.read_csv(input_path)

# ---------- 2) Convert month to datetime ----------
# Assuming format like 2025-12 or similar
df["Month_dt"] = pd.to_datetime(df["Month"], errors="coerce")

# ---------- 3) Basic features ----------

# Extract year and month number
df["year"] = df["Month_dt"].dt.year
df["month_num"] = df["Month_dt"].dt.month

# Month-over-month growth inside each branch
df = df.sort_values(["Branch", "Month_dt"])

df["monthly_growth_rate"] = (
    df.groupby("Branch")["Total_Sales"]
      .pct_change()
)

# Share of branch in total company sales (per month)
monthly_total = df.groupby("Month_dt")["Total_Sales"].transform("sum")
df["branch_share_that_month"] = df["Total_Sales"] / monthly_total

# ---------- 4) Quick check ----------
print(df.head())

# ---------- 5) Save ----------
df.to_csv(output_path, index=False)
print("Saved:", output_path)