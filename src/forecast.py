from __future__ import annotations

from datetime import timedelta
from typing import Dict, Any, List
from pathlib import Path

import pandas as pd

# -------------------------------------------------------------------
# 1) EXACT DATA FILE PATH YOU GAVE ME
# -------------------------------------------------------------------

DATA_FILE = Path(
    r"C:\Users\user\Desktop\conut-chief-operations-agent\conut-chief-operations-agent\data\prepared data\model_ready\model_branch_daily_ops.csv"
)

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Data file not found at: {DATA_FILE}")


# -------------------------------------------------------------------
# 2) FORECAST FUNCTION (USING Branch / Date / Total_Revenue)
# -------------------------------------------------------------------

def make_branch_forecast(
    df_daily: pd.DataFrame,
    branch_name: str,
    date_col: str = "Date",
    target_col: str = "Total_Revenue",
    branch_col: str = "Branch",
    horizon_days: int = 7,
    window_days: int = 14,
) -> Dict[str, Any]:
    """
    Simple rolling-mean forecast per branch.

    df_daily    : dataframe with columns Branch, Date, Total_Revenue
    branch_name : which Branch to forecast
    """

    # Make sure the needed columns exist
    required_cols = {date_col, target_col, branch_col}
    missing = required_cols - set(df_daily.columns)
    if missing:
        raise ValueError(f"Missing required columns in data: {missing}")

    # Filter for the requested branch
    df_branch = df_daily[df_daily[branch_col] == branch_name].copy()
    if df_branch.empty:
        raise ValueError(f"No data found for branch={branch_name!r}")

    # Ensure proper types and sort by date
    df_branch[date_col] = pd.to_datetime(df_branch[date_col])
    df_branch = df_branch.sort_values(date_col)

    # Rolling mean baseline over the last window_days
    df_branch["rolling_mean"] = (
        df_branch[target_col]
        .rolling(window=window_days, min_periods=max(3, window_days // 2))
        .mean()
    )

    baseline = df_branch["rolling_mean"].iloc[-1]
    if pd.isna(baseline):
        # fallback if history is too short
        baseline = df_branch[target_col].tail(window_days).mean()

    last_date = df_branch[date_col].max()

    # Build future forecast rows
    forecast_rows: List[Dict[str, Any]] = []
    for step in range(1, horizon_days + 1):
        future_date = last_date + timedelta(days=step)
        forecast_rows.append(
            {
                "date": future_date.date().isoformat(),
                "predicted_value": float(baseline),
            }
        )

    hist_series = df_branch[target_col]

    result: Dict[str, Any] = {
        "branch": str(branch_name),
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

    return result


# -------------------------------------------------------------------
# 3) MAIN: LOAD DATA & RUN FORECAST FOR ONE BRANCH
# -------------------------------------------------------------------

if __name__ == "__main__":
    print(f"[forecast] Loading data from: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)

    # Pick the first branch name in the file as a demo
    if "Branch" not in df.columns:
        raise ValueError("Expected a column named 'Branch' in the dataset.")

    example_branch = str(df["Branch"].iloc[0])
    print(f"[forecast] Example branch: {example_branch}")

    forecast_result = make_branch_forecast(
        df_daily=df,
        branch_name=example_branch,
        date_col="Date",
        target_col="Total_Revenue",
        branch_col="Branch",
        horizon_days=7,
        window_days=14,
    )

    print("\nForecast Result:\n")
    print(forecast_result)