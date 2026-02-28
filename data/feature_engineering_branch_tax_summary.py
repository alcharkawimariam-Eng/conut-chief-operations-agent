import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent  # .../conut-chief-operations-agent/data

input_path = BASE_DIR / "prepared data" / "cleaned_branch_tax_summary.csv"
output_path = BASE_DIR / "prepared data" / "branch_tax_features.csv"

# ---------- 1) Load data ----------
df = pd.read_csv(input_path)

# ---------- 2) Overall totals ----------
# Total revenue across all branches (for relative comparisons)
total_revenue_all = df["Total_Revenue"].sum()

# Share of revenue each branch contributes to the whole business
df["revenue_share_overall"] = df["Total_Revenue"] / total_revenue_all

# ---------- 3) Ranking & tiers ----------
# Rank branches by revenue (1 = highest revenue)
df["revenue_rank"] = df["Total_Revenue"].rank(
    ascending=False, method="dense"
).astype(int)

# Percentile (0–1): where this branch stands vs others
df["revenue_percentile"] = df["Total_Revenue"].rank(pct=True)

def revenue_tier(p):
    if p >= 0.8:
        return "top"
    elif p >= 0.5:
        return "mid"
    else:
        return "low"

df["revenue_tier"] = df["revenue_percentile"].apply(revenue_tier)

# ---------- 4) VAT vs revenue ----------
# Safety check feature: how much VAT compared to revenue
df["vat_to_revenue_ratio"] = df["VAT_11_Percent"] / df["Total_Revenue"]

# ---------- 5) Quick check ----------
print(df.head())

# ---------- 6) Save ----------
df.to_csv(output_path, index=False)
print("Saved:", output_path)