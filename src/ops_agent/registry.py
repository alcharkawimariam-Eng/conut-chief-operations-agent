# src/ops_agent/registry.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ModelRegistry:
    forecast_model: Optional[Any] = None
    staffing_model: Optional[Any] = None
    combo_model: Optional[Any] = None
    expansion_model: Optional[Any] = None
    beverage_model: Optional[Any] = None

def load_registry() -> ModelRegistry:
    # Option A: Use your existing python modules (recommended first step)
    # You can also load .pkl/.joblib here later.

    reg = ModelRegistry()

    # Example: if you later want joblib:
    # import joblib
    # reg.forecast_model = joblib.load("models/forecast.pkl")

    return reg