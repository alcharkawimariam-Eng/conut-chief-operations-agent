import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent  # .../conut-chief-operations-agent/data

input_path = BASE_DIR / "prepared data" / "division_summary_clean.csv"
output_path = BASE_DIR / "prepared data" / "division_summary_features.csv"

# ---------- 1) Load ----------
df = pd.read_csv(input_path)

# ---------- 2) Ensure numeric ----------
for col in ["Delivery", "Table", "TakeAway", "Total"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------- 3) Branch-level totals ----------
# Total sales per branch (sum of all divisions)
df["branch_total_sales"] = df.groupby("Branch")["Total"].transform("sum")

# Share of each division in its branch
df["division_sales_share_in_branch"] = df["Total"] / df["branch_total_sales"]

# ---------- 4) Channel mix inside each division ----------
# Shares of delivery / table / takeaway inside that division
df["delivery_share"] = df["Delivery"] / df["Total"]
df["table_share"] = df["Table"] / df["Total"]
df["takeaway_share"] = df["TakeAway"] / df["Total"]

# ---------- 5) Ranking divisions inside each branch ----------
df["division_rank_in_branch"] = (
    df.groupby("Branch")["Total"]
      .rank(method="dense", ascending=False)
)

# Flag top 3 divisions per branch
df["is_top3_division_in_branch"] = (df["division_rank_in_branch"] <= 3).astype(int)

# ---------- 6) Quick check ----------
print(df.head())

# ---------- 7) Save ----------
df.to_csv(output_path, index=False)
print("Saved:", output_path)