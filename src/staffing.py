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
