import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent

input_path = BASE_DIR / "prepared data" / "cleaned_sales_by_item_group.csv"
output_path = BASE_DIR / "prepared data" / "sales_by_item_group_features.csv"

# ---------- 1) Load ----------
df = pd.read_csv(input_path)

# ---------- 2) Ensure numeric ----------
df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce")
df["Total_Amount"] = pd.to_numeric(df["Total_Amount"], errors="coerce")

# ---------- 3) Branch-level totals ----------
branch_total_sales = df.groupby("Branch")["Total_Amount"].transform("sum")
df["branch_total_sales"] = branch_total_sales

# ---------- 4) Item-level features ----------
# Price per unit for each item
df["unit_price"] = df["Total_Amount"] / df["Qty"]

# How much this item contributes to its branch sales
df["item_sales_share_in_branch"] = df["Total_Amount"] / df["branch_total_sales"]

# Rank items inside each branch by sales
df["item_rank_in_branch"] = (
    df.groupby("Branch")["Total_Amount"]
      .rank(method="dense", ascending=False)
)

# Flag top 10 items in each branch
df["is_top10_item_in_branch"] = (df["item_rank_in_branch"] <= 10).astype(int)

# ---------- 5) Group-level features ----------
# Total sales per (Branch, Group)
group_summary = (
    df.groupby(["Branch", "Group"], as_index=False)
      .agg(group_total_sales=("Total_Amount", "sum"))
)

# Rank groups inside each branch
group_summary["group_rank_in_branch"] = (
    group_summary.groupby("Branch")["group_total_sales"]
    .rank(method="dense", ascending=False)
)

# Flag top 3 groups in each branch
group_summary["is_top3_group_in_branch"] = (
    group_summary["group_rank_in_branch"] <= 3
).astype(int)

# Merge group info back to item level
df = df.merge(group_summary, on=["Branch", "Group"], how="left")

# Share of group inside branch (same value for all items in that group)
df["group_sales_share_in_branch"] = df["group_total_sales"] / df["branch_total_sales"]

# ---------- 6) Quick check ----------
print(df.head())

# ---------- 7) Save ----------
df.to_csv(output_path, index=False)
print("Saved:", output_path)