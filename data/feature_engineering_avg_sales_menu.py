import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent  # .../conut-chief-operations-agent/data

input_path = BASE_DIR / "prepared data" / "cleaned_avg_sales_menu.csv"
output_path = BASE_DIR / "prepared data" / "avg_sales_menu_features.csv"

# ---------- 1) Load data ----------
df = pd.read_csv(input_path)

# ---------- 2) Branch-level totals ----------
branch_totals = (
    df.groupby("Branch")
    .agg(
        branch_total_sales=("Total_Sales", "sum"),
        branch_total_customers=("Customer_Count", "sum"),
    )
    .reset_index()
)

# Join totals back to each row
df = df.merge(branch_totals, on="Branch", how="left")

# ---------- 3) Shares inside each branch ----------
# How much this menu type contributes to its branch
df["sales_share_in_branch"] = df["Total_Sales"] / df["branch_total_sales"]
df["customer_share_in_branch"] = df["Customer_Count"] / df["branch_total_customers"]

# ---------- 4) Premium menu flag (high avg spent vs branch median) ----------
branch_median_spent = df.groupby("Branch")["Avg_Spent_Per_Customer"].transform("median")
df["is_premium_menu_in_branch"] = (
    df["Avg_Spent_Per_Customer"] > branch_median_spent
).astype(int)

# ---------- 5) Quick check ----------
print(df.head())

# ---------- 6) Save ----------
df.to_csv(output_path, index=False)
print("Saved:", output_path)