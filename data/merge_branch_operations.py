import pandas as pd
from pathlib import Path
import numpy as np

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent

staffing_path = BASE_DIR / "prepared data" / "branch_daily_staffing_features.csv"
branch_master_path = BASE_DIR / "prepared data" / "branch_master_features.csv"
output_path = BASE_DIR / "prepared data" / "branch_daily_operations_features.csv"

# ---------- 1) Load ----------
staff = pd.read_csv(staffing_path)
branch_master = pd.read_csv(branch_master_path)

# Make sure Date is datetime (staffing file)
if "Date" in staff.columns:
    staff["Date"] = pd.to_datetime(staff["Date"], errors="coerce")

# ---------- 2) Extra staffing features ----------
# Avoid division by zero
staff["work_hours_per_employee"] = np.where(
    staff["num_employees"] > 0,
    staff["total_work_hours"] / staff["num_employees"],
    np.nan,
)

staff["employees_per_work_hour"] = np.where(
    staff["total_work_hours"] > 0,
    staff["num_employees"] / staff["total_work_hours"],
    np.nan,
)

# ---------- 3) Merge with branch master ----------
# This adds revenue & monthly sales statistics to every branch-day row
ops = staff.merge(branch_master, on="Branch", how="left")

# ---------- 4) Quick check ----------
print(ops.head())

# ---------- 5) Save ----------
ops.to_csv(output_path, index=False)
print("Saved:", output_path)