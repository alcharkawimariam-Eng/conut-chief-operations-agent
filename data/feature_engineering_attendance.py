import pandas as pd
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent
input_path = BASE_DIR / "prepared data" / "cleaned_attendance_logs.csv"
output_detailed = BASE_DIR / "prepared data" / "attendance_with_features.csv"
output_daily = BASE_DIR / "prepared data" / "branch_daily_staffing_features.csv"

# ---------- 1) Load ----------
df = pd.read_csv(input_path)

# ---------- 2) Fix types ----------
df["Employee_ID"] = df["Employee_ID"].astype("Int64")
df["Date"] = pd.to_datetime(df["Date"])

# ---------- 3) Calendar features ----------
df["day_of_week"] = df["Date"].dt.day_name()
df["day_of_week_num"] = df["Date"].dt.dayofweek
df["is_weekend"] = (df["day_of_week_num"] >= 5).astype(int)

# ---------- 4) Time features ----------
df["Punch_In_dt"] = pd.to_datetime(df["Punch_In"], format="%H.%M.%S", errors="coerce")
df["Punch_Out_dt"] = pd.to_datetime(df["Punch_Out"], format="%H.%M.%S", errors="coerce")

df["start_hour"] = df["Punch_In_dt"].dt.hour
df["end_hour"] = df["Punch_Out_dt"].dt.hour

def part_of_day(h):
    if pd.isna(h):
        return "unknown"
    h = int(h)
    if 5 <= h < 12:
        return "morning"
    elif 12 <= h < 17:
        return "afternoon"
    elif 17 <= h < 22:
        return "evening"
    else:
        return "night"

df["part_of_day"] = df["start_hour"].apply(part_of_day)

# ---------- 5) Save detailed ----------
df.to_csv(output_detailed, index=False)

# ---------- 6) Branch-day aggregation (KEY FOR STAFFING) ----------
branch_daily = (
    df.groupby(["Branch", "Date"])
    .agg(
        num_employees=("Employee_ID", "nunique"),
        total_work_hours=("Work_Hours", "sum"),
        avg_work_hours=("Work_Hours", "mean"),
        weekend=("is_weekend", "max")
    )
    .reset_index()
)

branch_daily.to_csv(output_daily, index=False)

print("Saved detailed file:", output_detailed)
print("Saved daily staffing file:", output_daily)
print(branch_daily.head())