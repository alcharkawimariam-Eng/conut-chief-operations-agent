from __future__ import annotations

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

print(f"[expansion] Using OPS_FILE: {OPS_FILE}")

# Load once
df_ops = pd.read_csv(OPS_FILE)


# -------------------------------------------------------------------
# 2) EXPANSION ANALYSIS PER BRANCH
# -------------------------------------------------------------------

def analyze_branch_for_expansion(
    branch_name: str,
    date_col: str = "Date",
    branch_col: str = "Branch",
    revenue_col: str = "Total_Revenue",
) -> Dict[str, Any]:
    """
    Analyze one branch for expansion feasibility.

    Simple logic:
    - Compute average daily revenue.
    - Split history into early and late periods.
    - Compute growth rate between early and late revenue.
    - Label trend + give a recommendation.
    """

    required_cols = {date_col, branch_col, revenue_col}
    missing = required_cols - set(df_ops.columns)
    if missing:
        raise ValueError(f"Missing required columns in ops data: {missing}")

    df_branch = df_ops[df_ops[branch_col] == branch_name].copy()
    if df_branch.empty:
        raise ValueError(f"No ops data found for branch={branch_name!r}")

    df_branch[date_col] = pd.to_datetime(df_branch[date_col])
    df_branch = df_branch.sort_values(date_col)

    n_days = len(df_branch)
    avg_revenue = float(df_branch[revenue_col].mean())

    # Split into early and late thirds to estimate trend
    if n_days < 6:
        # Not enough history: treat as flat
        early_mean = float(df_branch[revenue_col].iloc[: max(1, n_days // 2)].mean())
        late_mean = float(df_branch[revenue_col].iloc[max(1, n_days // 2) :].mean())
    else:
        third = n_days // 3
        early_mean = float(df_branch[revenue_col].iloc[:third].mean())
        late_mean = float(df_branch[revenue_col].iloc[-third:].mean())

    # Growth rate
    if abs(early_mean) < 1e-9:
        growth_rate = 0.0
    else:
        growth_rate = (late_mean - early_mean) / abs(early_mean)

    # Trend label
    if growth_rate > 0.15:
        trend = "strong_growth"
    elif growth_rate > 0.02:
        trend = "mild_growth"
    elif growth_rate < -0.10:
        trend = "decline"
    else:
        trend = "flat"

    # Simple scoring: combine average revenue and growth
    # (this is just a heuristic for the hackathon)
    revenue_score = 1
    if avg_revenue > 0:
        # rough thresholds; you can tune
        if avg_revenue > 0.75 * df_ops[revenue_col].max():
            revenue_score = 3
        elif avg_revenue > 0.40 * df_ops[revenue_col].max():
            revenue_score = 2
        else:
            revenue_score = 1

    if trend in ("strong_growth", "mild_growth"):
        trend_score = 2
    elif trend == "flat":
        trend_score = 1
    else:  # decline
        trend_score = 0

    expansion_score = revenue_score + trend_score

    if expansion_score >= 4:
        recommendation = "Strong candidate for expansion"
    elif expansion_score >= 2:
        recommendation = "Moderate candidate for expansion"
    else:
        recommendation = "Not a priority for expansion right now"

    return {
        "branch": branch_name,
        "n_days": int(n_days),
        "avg_daily_revenue": avg_revenue,
        "early_period_revenue": early_mean,
        "late_period_revenue": late_mean,
        "growth_rate": growth_rate,
        "trend": trend,
        "expansion_score": int(expansion_score),
        "expansion_recommendation": recommendation,
    }


def evaluate_expansion_all_branches() -> Dict[str, Any]:
    """
    Run expansion analysis for all branches in the ops data.
    """

    if "Branch" not in df_ops.columns:
        raise ValueError("Column 'Branch' not found in ops dataset.")

    branches = sorted(df_ops["Branch"].dropna().astype(str).unique())

    summaries: List[Dict[str, Any]] = []
    for br in branches:
        print(f"[expansion] Analyzing branch: {br}")
        try:
            summary = analyze_branch_for_expansion(br)
        except Exception as exc:
            print(f"[expansion] WARNING: failed for {br}: {exc}")
            continue
        summaries.append(summary)

    # Sort branches by expansion_score descending, then by avg_daily_revenue
    summaries.sort(
        key=lambda s: (s["expansion_score"], s["avg_daily_revenue"]),
        reverse=True,
    )

    return {"branches": summaries}


# -------------------------------------------------------------------
# 3) MAIN: DEMO RUN
# -------------------------------------------------------------------

if __name__ == "__main__":
    results = evaluate_expansion_all_branches()

    print("\n[expansion] Expansion feasibility summary:\n")
    print(results)