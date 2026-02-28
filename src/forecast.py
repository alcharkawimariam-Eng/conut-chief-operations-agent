# src/forecast.py
import pandas as pd

def forecast_branch(branch_id, horizon=30, file_path="data/clean/monthly_branch_sales_clean.csv"):
    """
    Simple demand forecast per branch using 7-day moving average.
    """
    try:
        df = pd.read_csv(file_path)
    except:
        return {"analysis_name": "demand_forecasting", "error": "Clean branch sales file not found yet"}

    if "date" not in df.columns or "branch_id" not in df.columns or "quantity" not in df.columns:
        return {"analysis_name": "demand_forecasting", "error": "Required columns missing"}

    branch_df = df[df["branch_id"] == branch_id].copy()
    if branch_df.empty:
        return {"analysis_name": "demand_forecasting", "error": f"No data for branch {branch_id}"}

    branch_df["date"] = pd.to_datetime(branch_df["date"])
    branch_df = branch_df.sort_values("date")
    branch_df["ma7"] = branch_df["quantity"].rolling(7).mean()
    last_ma = branch_df["ma7"].iloc[-1] if not pd.isna(branch_df["ma7"].iloc[-1]) else branch_df["quantity"].mean()

    forecast_values = [round(last_ma)] * horizon

    return {
        "analysis_name": "demand_forecasting",
        "inputs": {"branch_id": branch_id, "horizon": horizon},
        "key_findings": [f"Average daily demand (last 7 days) ≈ {last_ma:.1f}"],
        "recommendations": [f"Plan inventory for next {horizon} days ≈ {sum(forecast_values)} units"],
        "confidence": "medium",
        "forecast": forecast_values
    }
