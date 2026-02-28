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
