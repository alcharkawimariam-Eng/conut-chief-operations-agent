from __future__ import annotations

from typing import Dict, Any, List, Tuple
from pathlib import Path
from collections import Counter
import itertools

import pandas as pd

# -------------------------------------------------------------------
# 1) EXACT MODEL_READY PATH
# -------------------------------------------------------------------

MODEL_READY_DIR = Path(
    r"C:\Users\user\Desktop\conut-chief-operations-agent\conut-chief-operations-agent\data\prepared data\model_ready"
)

SALES_FILE = MODEL_READY_DIR / "model_sales_detail.csv"

if not SALES_FILE.exists():
    raise FileNotFoundError(f"Sales detail file not found at: {SALES_FILE}")

print(f"[combo] Using SALES_FILE: {SALES_FILE}")

# Load once at import time
df_sales = pd.read_csv(SALES_FILE)


# -------------------------------------------------------------------
# 2) MAIN LOGIC: COMBO SUGGESTIONS PER BRANCH
# -------------------------------------------------------------------

def suggest_combos_for_branch(
    branch_name: str,
    min_support: int = 2,
    top_n: int = 10,
) -> Dict[str, Any]:
    """
    Simple combo optimization for a given branch.

    Idea:
    - For each customer in this branch, collect the unique set of Items in their basket.
    - For each pair of items (A, B) in that basket, increment a counter.
    - Sort by frequency and return the top N combos.

    Parameters
    ----------
    branch_name : str
        Name of the branch (e.g. 'Conut - Tyre').
    min_support : int
        Minimum number of baskets in which a pair must appear to be considered.
    top_n : int
        Maximum number of combos to return.

    Returns
    -------
    Dict[str, Any]
        JSON-style object with branch name and list of combos.
    """

    required_cols = {"Branch", "Customer", "Item"}
    missing = required_cols - set(df_sales.columns)
    if missing:
        raise ValueError(f"Missing required columns in sales data: {missing}")

    # Filter to this branch
    df_branch = df_sales[df_sales["Branch"] == branch_name].copy()
    if df_branch.empty:
        raise ValueError(f"No sales data found for branch={branch_name!r}")

    # Group by "basket" (here we approximate basket by Customer within a branch)
    combos_counter: Counter[Tuple[str, str]] = Counter()

    for _, basket_df in df_branch.groupby("Customer"):
        # Unique items in this customer's purchases for this branch
        items = sorted(set(basket_df["Item"].astype(str).tolist()))
        if len(items) < 2:
            continue  # can't form a pair

        # All unique pairs of items in this basket
        for a, b in itertools.combinations(items, 2):
            combos_counter[(a, b)] += 1

    # Filter by minimum support (how many customers had this combo)
    filtered = [
        (pair, count)
        for pair, count in combos_counter.items()
        if count >= min_support
    ]

    # Sort by descending count
    filtered.sort(key=lambda x: x[1], reverse=True)

    # Take top N
    top_combos = filtered[:top_n]

    combos_list: List[Dict[str, Any]] = []
    for (item_a, item_b), count in top_combos:
        combos_list.append(
            {
                "item_a": item_a,
                "item_b": item_b,
                "support_customers": int(count),
            }
        )

    result: Dict[str, Any] = {
        "branch": branch_name,
        "min_support": min_support,
        "top_n": top_n,
        "n_combos_found": len(combos_list),
        "combos": combos_list,
    }
    return result


# -------------------------------------------------------------------
# 3) MAIN: DEMO RUN
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Pick a sample branch from the data
    if "Branch" not in df_sales.columns:
        raise ValueError("Column 'Branch' not found in sales detail dataset.")

    sample_branch = str(df_sales["Branch"].iloc[0])
    print(f"[combo] Example branch: {sample_branch}")

    combos = suggest_combos_for_branch(
        branch_name=sample_branch,
        min_support=2,
        top_n=10,
    )

    print("\n[combo] Combo suggestions:\n")
    print(combos)
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
