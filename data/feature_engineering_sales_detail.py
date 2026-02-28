import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent

input_path = BASE_DIR / "prepared data" / "cleaned_sales_detail.csv"
output_path = BASE_DIR / "prepared data" / "sales_detail_features.csv"

# ---------- 1) Load ----------
df = pd.read_csv(input_path)

# ---------- 2) Ensure numeric ----------
df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce")
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

# ---------- 3) Line-level features ----------
# Revenue of this line
df["line_total"] = df["Qty"] * df["Price"]

# ---------- 4) Coffee / Milkshake tagging ----------
df["Item_upper"] = df["Item"].str.upper()

def classify_item(name):
    if pd.isna(name):
        return "unknown"
    if "MILKSHAKE" in name:
        return "milkshake"
    if (
        "COFFEE" in name
        or "LATTE" in name
        or "ESPRESSO" in name
        or "CAPPUCCINO" in name
    ):
        return "coffee"
    return "other"

df["item_category"] = df["Item_upper"].apply(classify_item)
df["is_milkshake"] = (df["item_category"] == "milkshake").astype(int)
df["is_coffee"] = (df["item_category"] == "coffee").astype(int)
df["is_core_beverage"] = ((df["is_milkshake"] + df["is_coffee"]) > 0).astype(int)

# We don't need the helper column anymore
df.drop(columns=["Item_upper"], inplace=True)

# ---------- 5) Quick check ----------
print(df.head())

# ---------- 6) Save ----------
df.to_csv(output_path, index=False)
print("Saved:", output_path)