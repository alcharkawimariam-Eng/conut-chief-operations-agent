from __future__ import annotations

from datetime import timedelta
from typing import Dict, Any, List
from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# 1) EXACT MODEL_READY PATH
# -------------------------------------------------------------------

MODEL_READY_DIR = Path(
    r"C:\Users\user\Desktop\conut-chief-operations-agent\conut-chief-operations-agent\data\prepared data\model_ready"
)

OPS_FILE = MODEL_READY_DIR / "model_branch_daily_ops.csv"

if not OPS_FILE.exists():
    raise FileNotFoundError(f"Branch daily ops file not found at: {OPS_FILE}")

print(f"[staffing] Using OPS_FILE: {OPS_FILE}")

# Load once
df_ops = pd.read_csv(OPS_FILE)


# -------------------------------------------------------------------
# 2) STAFFING RECOMMENDATION PER BRANCH
# -------------------------------------------------------------------

def recommend_staffing_for_branch(
    branch_name: str,
    horizon_days: int = 7,
    workday_hours: float = 8.0,
    date_col: str = "Date",
    branch_col: str = "Branch",
    employees_col: str = "num_employees",
    revenue_col: str = "Total_Revenue",
    weekend_col: str = "weekend",
) -> Dict[str, Any]:
    """
    Simple staffing estimation based on historical revenue and staffing.

    Idea:
    - Compute historical revenue per employee for this branch.
    - Use median revenue/employee as a baseline.
    - Estimate typical weekday and weekend revenue.
    - For the next `horizon_days`, recommend employees per day:
        employees = round(expected_revenue / baseline_revenue_per_employee)

    Parameters
    ----------
    branch_name : str
        Branch name (e.g. 'Conut - Tyre').
    horizon_days : int
        Number of future days to generate staffing plan for.
    workday_hours : float
        Hours per employee per day (e.g. 8).

    Returns
    -------
    Dict[str, Any]
        JSON-style object with staffing recommendations per day.
    """

    required_cols = {date_col, branch_col, employees_col, revenue_col, weekend_col}
    missing = required_cols - set(df_ops.columns)
    if missing:
        raise ValueError(f"Missing required columns in ops data: {missing}")

    # Filter to this branch
    df_branch = df_ops[df_ops[branch_col] == branch_name].copy()
    if df_branch.empty:
        raise ValueError(f"No ops data found for branch={branch_name!r}")

    # Ensure datetime and sort
    df_branch[date_col] = pd.to_datetime(df_branch[date_col])
    df_branch = df_branch.sort_values(date_col)

    # Guard against zero employees
    df_branch[employees_col] = df_branch[employees_col].clip(lower=1)

    # Historical revenue per employee
    df_branch["revenue_per_employee"] = (
        df_branch[revenue_col] / df_branch[employees_col]
    )

    baseline_rpe = float(df_branch["revenue_per_employee"].median())

    # Split weekday vs weekend
    weekdays = df_branch[df_branch[weekend_col] == 0]
    weekends = df_branch[df_branch[weekend_col] == 1]

    if not weekdays.empty:
        weekday_rev = float(weekdays[revenue_col].mean())
    else:
        weekday_rev = float(df_branch[revenue_col].mean())

    if not weekends.empty:
        weekend_rev = float(weekends[revenue_col].mean())
    else:
        weekend_rev = float(df_branch[revenue_col].mean())

    # Last observed date in the dataset
    last_date = df_branch[date_col].max()

    # Build future staffing plan
    plan: List[Dict[str, Any]] = []
    for step in range(1, horizon_days + 1):
        future_date = last_date + timedelta(days=step)
        is_weekend = 1 if future_date.weekday() >= 5 else 0  # 5=Saturday,6=Sunday

        expected_revenue = weekend_rev if is_weekend else weekday_rev

        if baseline_rpe <= 0:
            # Fallback: use median employees
            employees_needed = int(round(float(df_branch[employees_col].median())))
        else:
            employees_needed = int(
                max(1, round(expected_revenue / baseline_rpe))
            )

        total_hours = employees_needed * workday_hours

        plan.append(
            {
                "date": future_date.date().isoformat(),
                "is_weekend": bool(is_weekend),
                "expected_revenue": float(expected_revenue),
                "recommended_employees": int(employees_needed),
                "total_work_hours": float(total_hours),
            }
        )

    result: Dict[str, Any] = {
        "branch": branch_name,
        "horizon_days": horizon_days,
        "workday_hours": workday_hours,
        "baseline_revenue_per_employee": baseline_rpe,
        "historical_days": int(len(df_branch)),
        "staffing_plan": plan,
    }

    return result


# -------------------------------------------------------------------
# 3) MAIN: DEMO RUN
# -------------------------------------------------------------------

if __name__ == "__main__":
    if "Branch" not in df_ops.columns:
        raise ValueError("Column 'Branch' not found in ops dataset.")

    sample_branch = str(df_ops["Branch"].iloc[0])
    print(f"[staffing] Example branch: {sample_branch}")

    staffing_plan = recommend_staffing_for_branch(
        branch_name=sample_branch,
        horizon_days=7,
        workday_hours=8.0,
    )

    print("\n[staffing] Staffing recommendation:\n")
    print(staffing_plan)
# src/staffing.py
import pandas as pd

def estimate_staff(branch_id, day_of_week, file_path="data/clean/attendance_clean.csv"):
    """
    Estimate number of staff needed per shift using past attendance.
    """
    try:
        df = pd.read_csv(file_path)
    except:
        return {"analysis_name": "staffing_estimation", "error": "Clean attendance file not found yet"}

    if "branch_id" not in df.columns or "date" not in df.columns or "shift" not in df.columns:
        return {"analysis_name": "staffing_estimation", "error": "Required columns missing"}

    # Simple placeholder: average staff per branch
    avg_staff = df[df["branch_id"] == branch_id]["employee_id"].nunique()
    if avg_staff == 0:
        avg_staff = 5  # fallback default

    return {
        "analysis_name": "staffing_estimation",
        "inputs": {"branch_id": branch_id, "day_of_week": day_of_week},
        "key_findings": [f"Average staff needed ≈ {avg_staff}"],
        "recommendations": [f"Schedule ~{avg_staff} staff for {day_of_week}"],
        "confidence": "medium"
    }
