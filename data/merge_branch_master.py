import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent

tax_path = BASE_DIR / "prepared data" / "branch_tax_features.csv"
monthly_path = BASE_DIR / "prepared data" / "monthly_branch_sales_features.csv"
output_path = BASE_DIR / "prepared data" / "branch_master_features.csv"

# ---------- 1) Load ----------
tax = pd.read_csv(tax_path)
monthly = pd.read_csv(monthly_path)

# ---------- 2) Build branch-level sales stats from monthly data ----------
# We assume monthly file has columns:
#   Branch, Month, Total_Sales, monthly_growth_rate, ...
branch_sales_stats = (
    monthly.groupby("Branch")
    .agg(
        avg_monthly_sales=("Total_Sales", "mean"),
        max_monthly_sales=("Total_Sales", "max"),
        min_monthly_sales=("Total_Sales", "min"),
        std_monthly_sales=("Total_Sales", "std"),
        avg_monthly_growth=("monthly_growth_rate", "mean"),
    )
    .reset_index()
)

# ---------- 3) Merge tax + sales stats ----------
branch_master = tax.merge(branch_sales_stats, on="Branch", how="left")

# ---------- 4) Quick check ----------
print(branch_master.head())

# ---------- 5) Save ----------
branch_master.to_csv(output_path, index=False)
print("Saved:", output_path)