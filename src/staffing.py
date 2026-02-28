<<<<<<< HEAD
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
=======
# staffing.py
import pandas as pd

def estimate_staff(branch_name, day_of_week=None, hour_block=None):
    try:
        df = pd.read_csv("data/prepared/cleaned_attendance_logs.csv")
    except FileNotFoundError:
        return {"analysis_name": "staffing_estimation", "error": "Clean attendance file not found yet"}

    # Strip any extra spaces in branch names
    df['Branch'] = df['Branch'].str.strip()

    # Filter by the correct branch column
    branch_df = df[df['Branch'] == branch_name]

    # Sum total hours using the correct column
    total_hours = branch_df['Work_Hours'].sum() if not branch_df.empty else 0

    return {
        "analysis_name": "staffing_estimation",
        "inputs": {"branch_name": branch_name, "day_of_week": day_of_week, "hour_block": hour_block},
        "key_findings": [f"Total staff hours logged: {total_hours}"],
        "recommendations": ["Schedule staff according to forecasted demand"],
        "confidence": "medium"
    }
>>>>>>> main
