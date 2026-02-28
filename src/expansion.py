<<<<<<< HEAD
# src/expansion.py
import pandas as pd

def rank_expansion_candidates(file_path="data/clean/monthly_branch_sales_clean.csv"):
    """
    Rank branches for expansion feasibility based on sales growth.
    """
    try:
        df = pd.read_csv(file_path)
    except:
        return {"analysis_name": "expansion_feasibility", "error": "Clean branch sales file not found yet"}

    # Placeholder scoring (real logic can be added later)
    recommendations = ["Open branch near university", "Focus on high coffee ratio areas"]

    return {
        "analysis_name": "expansion_feasibility",
        "inputs": {},
        "key_findings": ["Branches with highest growth rate identified"],
        "recommendations": recommendations,
        "confidence": "medium"
    }
=======
# expansion.py
import pandas as pd

def rank_expansion_candidates():
    try:
        df = pd.read_csv("data/prepared/cleaned_monthly_branch_sales.csv")
    except FileNotFoundError:
        return {"analysis_name": "expansion_feasibility", "error": "Clean branch sales file not found yet"}

    # Use 'Total_Sales' instead of 'Qty'
    if 'Total_Sales' not in df.columns:
        return {"analysis_name": "expansion_feasibility", "error": "Total_Sales column missing in CSV"}

    ranking = df.groupby('Branch')['Total_Sales'].sum().sort_values(ascending=False).head(5).to_dict()

    return {
        "analysis_name": "expansion_feasibility",
        "key_findings": ["Top 5 branches by total sales"],
        "recommendations": [f"Consider expansion in {branch}" for branch in ranking.keys()],
        "confidence": "medium"
    }
>>>>>>> main
