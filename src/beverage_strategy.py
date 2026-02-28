<<<<<<< HEAD
# src/beverage_strategy.py
def coffee_milkshake_actions():
    """
    Recommend strategies to increase beverage sales.
    """
    return {
        "analysis_name": "beverage_growth_strategy",
        "inputs": {},
        "key_findings": ["Coffee and milkshake sales analyzed"],
=======
import pandas as pd

def coffee_milkshake_actions():
    file_path = "data/prepared/cleaned_sales_detail.csv"
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"analysis_name": "beverage_growth_strategy", "error": f"{file_path} not found"}

    coffee_sales = df[df['Item'].str.contains("Coffee", case=False)]
    milkshake_sales = df[df['Item'].str.contains("Milkshake", case=False)]

    return {
        "analysis_name": "beverage_growth_strategy",
        "inputs": {},
        "key_findings": [
            f"Total coffee sales: {coffee_sales['Qty'].sum()}",
            f"Total milkshake sales: {milkshake_sales['Qty'].sum()}"
        ],
>>>>>>> main
        "recommendations": [
            "Offer 3-5pm coffee + donut combos",
            "Promote milkshake specials during weekends"
        ],
        "confidence": "medium"
<<<<<<< HEAD
    }
=======
    }
>>>>>>> main
