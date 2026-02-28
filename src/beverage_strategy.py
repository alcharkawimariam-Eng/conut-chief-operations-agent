from __future__ import annotations

from typing import Dict, Any, List, Tuple

import pandas as pd


def analyze_beverage_growth(
    df_sales: pd.DataFrame,
    branch_id: str | None = None,
    date_col: str = "date",
    branch_col: str = "branch_id",
    category_col: str = "category",
    sales_col: str = "net_sales",
    beverage_categories: Tuple[str, str] = ("Coffee", "Milkshake"),
) -> Dict[str, Any]:
    """
    High-level strategy view for coffee & milkshake performance.

    Expected grain:
        One row per (branch, date, category) with sales.

    We compute:
        - Overall beverage share in total sales
        - Growth of beverage sales vs. rest of menu
        - Coffee vs. Milkshake mix
        - Simple recommendations text

    Parameters
    ----------
    df_sales : pd.DataFrame
        Historical sales data.
    branch_id : str | None
        If provided, filter to this branch. If None, use all branches.
    date_col : str
        Column with date.
    branch_col : str
        Column with branch id.
    category_col : str
        Column with product category (e.g. 'Coffee', 'Milkshake', 'Donut', ...).
    sales_col : str
        Column with numeric sales value.
    beverage_categories : (str, str)
        Names of the two beverage categories of interest.

    Returns
    -------
    Dict[str, Any]
        JSON-ready summary and a list of suggested actions.
    """

    required_cols = {date_col, branch_col, category_col, sales_col}
    missing = required_cols - set(df_sales.columns)
    if missing:
        raise ValueError(f"Missing required columns in sales data: {missing}")

    df = df_sales.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    if branch_id is not None:
        df = df[df[branch_col] == branch_id]
        if df.empty:
            raise ValueError(f"No data found for branch_id={branch_id!r}")

    cat_bev_1, cat_bev_2 = beverage_categories

    # Mark beverage vs non-beverage
    df["is_beverage"] = df[category_col].isin([cat_bev_1, cat_bev_2])

    # Monthly view for smoother trends
    df["month"] = df[date_col].dt.to_period("M").dt.to_timestamp()

    monthly_totals = (
        df.groupby("month")[sales_col]
        .sum()
        .rename("total_sales")
        .reset_index()
    )

    monthly_bev = (
        df[df["is_beverage"]]
        .groupby("month")[sales_col]
        .sum()
        .rename("beverage_sales")
        .reset_index()
    )

    monthly = pd.merge(monthly_totals, monthly_bev, on="month", how="left").fillna(0.0)
    monthly["beverage_share"] = (
        monthly["beverage_sales"] / monthly["total_sales"].where(monthly["total_sales"] > 0, 1.0)
    )

    # Coffee vs Milkshake split
    bev_detail = (
        df[df["is_beverage"]]
        .groupby(["month", category_col])[sales_col]
        .sum()
        .reset_index()
    )

    # Simple growth metrics (first vs last month)
    if len(monthly) >= 2:
        first = monthly.iloc[0]
        last = monthly.iloc[-1]
        bev_growth_abs = last["beverage_sales"] - first["beverage_sales"]
        bev_growth_pct = (
            (last["beverage_sales"] / first["beverage_sales"] - 1.0)
            if first["beverage_sales"] > 0
            else None
        )
        share_change = last["beverage_share"] - first["beverage_share"]
    else:
        bev_growth_abs = 0.0
        bev_growth_pct = None
        share_change = 0.0

    # Coffee vs milkshake last-month split
    last_month = monthly["month"].max()
    last_detail = bev_detail[bev_detail["month"] == last_month]

    coffee_sales = float(
        last_detail.loc[last_detail[category_col] == cat_bev_1, sales_col].sum()
    )
    milkshake_sales = float(
        last_detail.loc[last_detail[category_col] == cat_bev_2, sales_col].sum()
    )
    total_bev_last = coffee_sales + milkshake_sales
    coffee_share_last = (
        coffee_sales / total_bev_last if total_bev_last > 0 else 0.0
    )
    milkshake_share_last = (
        milkshake_sales / total_bev_last if total_bev_last > 0 else 0.0
    )

    # Build recommendations in plain language
    recommendations: List[str] = []

    if bev_growth_pct is not None and bev_growth_pct > 0.1:
        recommendations.append(
            "Beverage sales are growing strongly; double-down on coffee and milkshake upselling at the counter and in the app."
        )
    elif bev_growth_pct is not None and bev_growth_pct < -0.05:
        recommendations.append(
            "Beverage sales are declining; review pricing, promotions, and product positioning vs. donuts and other items."
        )

    if share_change > 0.02:
        recommendations.append(
            "Beverages are taking a larger share of the ticket; consider launching dedicated coffee/milkshake bundles."
        )
    elif share_change < -0.02:
        recommendations.append(
            "Beverages are losing share; add combo discounts that include at least one drink."
        )

    if coffee_share_last > 0.7:
        recommendations.append(
            "Coffee dominates within beverages; experiment with cross-promotions to grow milkshake sales, especially in warmer hours or seasons."
        )
    elif milkshake_share_last > 0.6:
        recommendations.append(
            "Milkshakes are leading; test premium coffee offers or loyalty stamps to lift coffee sales."
        )
    else:
        recommendations.append(
            "Coffee and milkshake are balanced; continue A/B testing different beverage-led bundles to maximize basket size."
        )

    summary: Dict[str, Any] = {
        "scope": "single_branch" if branch_id is not None else "all_branches",
        "branch_id": branch_id,
        "beverage_categories": [cat_bev_1, cat_bev_2],
        "overall": {
            "n_months": int(len(monthly)),
            "first_month": monthly["month"].min().date().isoformat(),
            "last_month": monthly["month"].max().date().isoformat(),
            "first_beverage_sales": float(monthly["beverage_sales"].iloc[0]),
            "last_beverage_sales": float(monthly["beverage_sales"].iloc[-1]),
            "beverage_sales_growth_abs": float(bev_growth_abs),
            "beverage_sales_growth_pct": float(bev_growth_pct) if bev_growth_pct is not None else None,
            "first_beverage_share": float(monthly["beverage_share"].iloc[0]),
            "last_beverage_share": float(monthly["beverage_share"].iloc[-1]),
            "beverage_share_change": float(share_change),
        },
        "last_month_split": {
            "month": last_month.date().isoformat(),
            "coffee_sales": coffee_sales,
            "milkshake_sales": milkshake_sales,
            "coffee_share": coffee_share_last,
            "milkshake_share": milkshake_share_last,
        },
        "recommendations": recommendations,
    }

    return summary
# src/beverage_strategy.py
def coffee_milkshake_actions():
    """
    Recommend strategies to increase beverage sales.
    """
    return {
        "analysis_name": "beverage_growth_strategy",
        "inputs": {},
        "key_findings": ["Coffee and milkshake sales analyzed"],
        "recommendations": [
            "Offer 3-5pm coffee + donut combos",
            "Promote milkshake specials during weekends"
        ],
        "confidence": "medium"
    }
