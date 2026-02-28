# src/combo.py
import pandas as pd
from itertools import combinations
from collections import Counter

def get_top_combos(file_path="data/clean/sales_line_items_clean.csv", top_k=10):
    """
    Returns top product combos using pair counts.
    Uses date + branch_id as a pseudo transaction ID.
    """
    try:
        df = pd.read_csv(file_path)
    except:
        return {"analysis_name": "combo_optimization", "error": "Clean sales file not found yet"}

    if "item_name" not in df.columns or "date" not in df.columns or "branch_id" not in df.columns:
        return {"analysis_name": "combo_optimization", "error": "Required columns missing"}

    # Create pseudo transaction ID
    df["transaction_id"] = df["date"].astype(str) + "_" + df["branch_id"].astype(str)
    transactions = df.groupby("transaction_id")["item_name"].apply(list)

    combo_counts = Counter()
    for items in transactions:
        for pair in combinations(set(items), 2):
            combo_counts[pair] += 1

    top_combos = combo_counts.most_common(top_k)

    return {
        "analysis_name": "combo_optimization",
        "key_findings": [{"items": list(pair), "count": count} for pair, count in top_combos],
        "recommendations": [
            "Create bundle offers for top item pairs",
            "Place combo items near each other in menu"
        ],
        "confidence": "medium"
    }
