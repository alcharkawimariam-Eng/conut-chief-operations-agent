<<<<<<< HEAD
"""
combo.py
Find best product combos for Conut.
"""

=======
>>>>>>> main
import pandas as pd
from itertools import combinations
from collections import Counter

<<<<<<< HEAD
def get_top_combos(file_path="data/clean/sales_line_items_clean.csv", top_k=10):
    """
    Returns top product combos.
    """

    try:
        df = pd.read_csv(file_path)
    except:
        return {
            "analysis_name": "combo_optimization",
            "error": "Clean sales file not found yet"
        }

    # Expect columns: transaction_id, item_name
    if "transaction_id" not in df.columns or "item_name" not in df.columns:
        return {
            "analysis_name": "combo_optimization",
            "error": "Required columns missing"
        }

    # Group items per transaction
    transactions = df.groupby("transaction_id")["item_name"].apply(list)

    combo_counts = Counter()

=======
def get_top_combos(file_path="data/prepared/cleaned_sales_detail.csv", top_k=10):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"analysis_name": "combo_optimization", "error": f"{file_path} not found"}

    if 'Customer' not in df.columns or 'Item' not in df.columns:
        return {"analysis_name": "combo_optimization", "error": "Required columns missing"}

    transactions = df.groupby('Customer')['Item'].apply(list)

    combo_counts = Counter()
>>>>>>> main
    for items in transactions:
        for pair in combinations(set(items), 2):
            combo_counts[pair] += 1

    top_combos = combo_counts.most_common(top_k)

    return {
        "analysis_name": "combo_optimization",
<<<<<<< HEAD
        "key_findings": [
            {"items": list(pair), "count": count}
            for pair, count in top_combos
        ],
        "recommendations": [
            "Create bundle offers for top item pairs",
            "Place combo items near each other in menu"
        ],
        "confidence": "medium"
    }
=======
        "key_findings": [{"items": list(pair), "count": count} for pair, count in top_combos],
        "recommendations": ["Create bundle offers for top item pairs", "Place combo items near each other"],
        "confidence": "medium"
    }
>>>>>>> main
