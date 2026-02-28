from __future__ import annotations

from datetime import timedelta
from typing import Dict, Any, List
from pathlib import Path
import json

import pandas as pd

# -------------------------------------------------------------------
# 1) EXACT MODEL_READY PATH YOU GAVE ME
# -------------------------------------------------------------------

MODEL_READY_DIR = Path(
    r"C:\Users\user\Desktop\conut-chief-operations-agent\conut-chief-operations-agent\data\prepared data\model_ready"
)

if not MODEL_READY_DIR.exists():
    raise FileNotFoundError(f"model_ready folder not found at: {MODEL_READY_DIR}")

print(f"[branch_json_export] Using MODEL_READY_DIR: {MODEL_READY_DIR}")


# -------------------------------------------------------------------
# 2) SAFE LOADER FOR EACH FILE
# -------------------------------------------------------------------

def load_if_exists(filename: str) -> pd.DataFrame | None:
    path = MODEL_READY_DIR / filename
    if path.exists():
        print(f"[branch_json_export] Loading: {path.name}")
        return pd.read_csv(path)
    else:
        print(f"[branch_json_export] WARNING: {filename} not found, skipping.")
        return None


df_ops = load_if_exists("model_branch_daily_ops.csv")
df_avg_menu = load_if_exists("model_avg_menu.csv")
df_sales_detail = load_if_exists("model_sales_detail.csv")
df_branch_master = load_if_exists("model_branch_master.csv")
df_customers = load_if_exists("model_customers.csv")
df_divisions = load_if_exists("model_divisions.csv")
df_item_groups = load_if_exists("model_item_groups.csv")


# -------------------------------------------------------------------
# 3) FORECAST FUNCTION (Total_Revenue, per branch)
# -------------------------------------------------------------------

def make_branch_revenue_forecast(
    df_daily_ops: pd.DataFrame,
    branch_name: str,
    date_col: str = "Date",
    target_col: str = "Total_Revenue",
    branch_col: str = "Branch",
    horizon_days: int = 7,
    window_days: int = 14,
) -> Dict[str, Any]:
    """
    Simple rolling-mean forecast of Total_Revenue for one branch.
    """

    required_cols = {date_col, target_col, branch_col}
    missing = required_cols - set(df_daily_ops.columns)
    if missing:
        raise ValueError(f"Missing required columns in ops data: {missing}")

    df_branch = df_daily_ops[df_daily_ops[branch_col] == branch_name].copy()
    if df_branch.empty:
        raise ValueError(f"No ops data found for branch={branch_name!r}")

    df_branch[date_col] = pd.to_datetime(df_branch[date_col])
    df_branch = df_branch.sort_values(date_col)

    df_branch["rolling_mean"] = (
        df_branch[target_col]
        .rolling(window=window_days, min_periods=max(3, window_days // 2))
        .mean()
    )

    baseline = df_branch["rolling_mean"].iloc[-1]
    if pd.isna(baseline):
        baseline = df_branch[target_col].tail(window_days).mean()

    last_date = df_branch[date_col].max()

    forecast_rows: List[Dict[str, Any]] = []
    for step in range(1, horizon_days + 1):
        future_date = last_date + timedelta(days=step)
        forecast_rows.append(
            {
                "date": future_date.date().isoformat(),
                "predicted_total_revenue": float(baseline),
            }
        )

    hist_series = df_branch[target_col]

    return {
        "branch": branch_name,
        "target_metric": target_col,
        "horizon_days": horizon_days,
        "method": f"rolling_mean_{window_days}_days",
        "historical_summary": {
            "n_days": int(len(hist_series)),
            "mean": float(hist_series.mean()),
            "std": float(hist_series.std() if len(hist_series) > 1 else 0.0),
            "min": float(hist_series.min()),
            "max": float(hist_series.max()),
            "last_observed_date": last_date.date().isoformat(),
            "last_observed_value": float(hist_series.iloc[-1]),
        },
        "forecast": forecast_rows,
    }


# -------------------------------------------------------------------
# 4) BUILD PER-BRANCH JSON OBJECT
# -------------------------------------------------------------------

def get_all_branches() -> List[str]:
    branch_sets: list[set[str]] = []

    for df in [df_ops, df_avg_menu, df_sales_detail,
               df_branch_master, df_customers, df_item_groups]:
        if df is not None and "Branch" in df.columns:
            branch_sets.append(set(df["Branch"].dropna().astype(str).unique()))

    if not branch_sets:
        raise RuntimeError("No Branch column found in any dataset.")

    all_branches = sorted(set().union(*branch_sets))
    print(f"[branch_json_export] Found {len(all_branches)} branches.")
    return all_branches


def filter_df(df: pd.DataFrame | None, branch: str) -> List[Dict[str, Any]]:
    if df is None:
        return []
    if "Branch" not in df.columns:
        return []
    rows = df[df["Branch"] == branch].copy()
    if rows.empty:
        return []
    return rows.to_dict(orient="records")


def build_branch_objects() -> Dict[str, Any]:
    branches_output: List[Dict[str, Any]] = []

    branches = get_all_branches()

    for br in branches:
        print(f"[branch_json_export] Processing branch: {br}")
        branch_obj: Dict[str, Any] = {"branch": br}

        # Raw data slices
        branch_obj["branch_daily_ops"] = filter_df(df_ops, br)
        branch_obj["avg_menu"] = filter_df(df_avg_menu, br)
        branch_obj["sales_detail"] = filter_df(df_sales_detail, br)
        branch_obj["branch_master"] = filter_df(df_branch_master, br)
        branch_obj["customers"] = filter_df(df_customers, br)
        branch_obj["divisions"] = filter_df(df_divisions, br)
        branch_obj["item_groups"] = filter_df(df_item_groups, br)

        # Revenue forecast (only if ops data is available)
        if df_ops is not None and branch_obj["branch_daily_ops"]:
            try:
                forecast = make_branch_revenue_forecast(df_ops, br)
            except Exception as exc:  # keep it safe
                print(f"[branch_json_export] WARNING: forecast failed for {br}: {exc}")
                forecast = None
        else:
            forecast = None

        branch_obj["revenue_forecast"] = forecast

        branches_output.append(branch_obj)

    return {"branches": branches_output}


# -------------------------------------------------------------------
# 5) MAIN: WRITE JSON FILE
# -------------------------------------------------------------------

if __name__ == "__main__":
    data = build_branch_objects()

    out_path = MODEL_READY_DIR / "branches_full_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[branch_json_export] Wrote JSON file to: {out_path}")