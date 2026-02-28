import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent
prepared_dir = BASE_DIR / "prepared data"
model_dir = prepared_dir / "model_ready"

model_dir.mkdir(exist_ok=True)

# ---------- Files to export ----------
# left = source filename in prepared data
# right = new, clean name in model_ready
files_map = {
    "branch_master_features.csv": "model_branch_master.csv",
    "branch_daily_operations_features.csv": "model_branch_daily_ops.csv",
    "customer_orders_features.csv": "model_customers.csv",
    "sales_by_item_group_features.csv": "model_item_groups.csv",
    "sales_detail_features.csv": "model_sales_detail.csv",
    "avg_sales_menu_features.csv": "model_avg_menu.csv",
    "division_summary_features.csv": "model_divisions.csv",
}

for src_name, dst_name in files_map.items():
    src_path = prepared_dir / src_name
    if not src_path.exists():
        print(f"WARNING: {src_name} not found, skipping.")
        continue

    df = pd.read_csv(src_path)
    dst_path = model_dir / dst_name
    df.to_csv(dst_path, index=False)
    print(f"Saved {dst_name} to model_ready")

print("Done exporting model-ready files.")