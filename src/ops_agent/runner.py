# src/ops_agent/runner.py
from __future__ import annotations

import importlib
import inspect
from typing import Any, Callable, Dict, List, Optional

from .router import Intent

# Candidate function names to try inside each module (ordered)
FORECAST_FUNCS = ["predict", "forecast", "run", "infer", "main", "make_branch_forecast"]
STAFFING_FUNCS = ["recommend", "staffing", "predict", "run", "infer", "main"]
COMBO_FUNCS    = ["best_combo", "recommend", "combo", "predict", "run", "main"]
EXPANSION_FUNCS= ["recommend", "expansion", "predict", "run", "main"]
BEV_FUNCS      = ["recommend", "beverage_strategy", "predict", "run", "main"]

def _import_any(names: List[str]):
    last_err = None
    for n in names:
        try:
            return importlib.import_module(n)
        except Exception as e:
            last_err = e
    raise last_err  # type: ignore

def _pick_callable(module, candidates: List[str]) -> Optional[Callable[..., Any]]:
    for name in candidates:
        fn = getattr(module, name, None)
        if callable(fn):
            return fn
    return None

def _call_safely(fn: Callable[..., Any], params: Dict[str, Any]) -> Any:
    """
    Calls fn with only the kwargs it accepts.
    """
    sig = inspect.signature(fn)
    allowed = set(sig.parameters.keys())

    # Keep only parameters that exist in function signature
    kwargs = {k: v for k, v in params.items() if v is not None and k in allowed}

    # If function takes no kwargs, call it with no args
    if len(allowed) == 0:
        return fn()

    # If function accepts **kwargs, pass all non-null params
    for p in sig.parameters.values():
        if p.kind == inspect.Parameter.VAR_KEYWORD:
            kwargs = {k: v for k, v in params.items() if v is not None}
            break

    return fn(**kwargs)

def run_intent(intent: Intent) -> Dict[str, Any]:
    """
    Returns a dict result that formatter.py can turn into exec text.
    """

    # Fallback
    if intent.name == "general":
        return {
            "type": "general",
            "message": (
                "I can help with: forecast, staffing, combos, expansion, and beverage strategy.\n"
                "Examples:\n"
                "- forecast B1 2026-03-05\n"
                "- staffing B2 shift A\n"
                "- best combo for B1\n"
                "- expansion recommendation\n"
                "- beverage strategy for B3"
            ),
        }

    # Import modules from src.*
        # Import ONLY the needed module (so one broken module doesn't break everything)
    try:
        if intent.name == "forecast":
            forecast_mod = _import_any(["src.forecast"])
        elif intent.name == "staffing":
            staffing_mod = _import_any(["src.staffing"])
        elif intent.name == "combo":
            combo_mod = _import_any(["src.combo"])
        elif intent.name == "expansion":
            expansion_mod = _import_any(["src.expansion"])
        elif intent.name == "beverage_strategy":
            bev_mod = _import_any(["src.beverage_strategy"])
        else:
            return {"type": "general", "message": f"Unknown intent: {intent.name}"}
    except Exception as e:
        return {
            "type": "general",
            "message": f"Model import error ({intent.name}): {type(e).__name__}: {e}",
        }
    params = intent.params or {}

    try:
        if intent.name == "forecast":
            fn = _pick_callable(forecast_mod, FORECAST_FUNCS)
            if not fn:
                return {"type": "general", "message": "forecast.py loaded but no callable found (tried: predict/forecast/run/infer/main)."}
            raw = _call_safely(fn, params)
            return _wrap_result(intent, raw)

        if intent.name == "staffing":
            fn = _pick_callable(staffing_mod, STAFFING_FUNCS)
            if not fn:
                return {"type": "general", "message": "staffing.py loaded but no callable found (tried: recommend/staffing/predict/run/infer/main)."}
            raw = _call_safely(fn, params)
            return _wrap_result(intent, raw)

        if intent.name == "combo":
            fn = _pick_callable(combo_mod, COMBO_FUNCS)
            if not fn:
                return {"type": "general", "message": "combo.py loaded but no callable found (tried: best_combo/recommend/combo/predict/run/main)."}
            raw = _call_safely(fn, params)
            return _wrap_result(intent, raw)

        if intent.name == "expansion":
            fn = _pick_callable(expansion_mod, EXPANSION_FUNCS)
            if not fn:
                return {"type": "general", "message": "expansion.py loaded but no callable found (tried: recommend/expansion/predict/run/main)."}
            raw = _call_safely(fn, params)
            return _wrap_result(intent, raw)

        if intent.name == "beverage_strategy":
            fn = _pick_callable(bev_mod, BEV_FUNCS)
            if not fn:
                return {"type": "general", "message": "beverage_strategy.py loaded but no callable found (tried: recommend/beverage_strategy/predict/run/main)."}
            raw = _call_safely(fn, params)
            return _wrap_result(intent, raw)

        return {"type": "general", "message": f"Unknown intent: {intent.name}"}

    except Exception as e:
        return {"type": "general", "message": f"Model execution error ({intent.name}): {type(e).__name__}: {e}"}

def _wrap_result(intent: Intent, raw: Any) -> Dict[str, Any]:
    """
    Normalize output into a dict for formatter.
    - If raw already a dict, keep it.
    - If raw is string/number/list, wrap as text.
    """
    if isinstance(raw, dict):
        raw.setdefault("confidence", intent.confidence)
        return raw

    return {
        "text": str(raw),
        "confidence": intent.confidence,
    }