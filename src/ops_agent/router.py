# src/ops_agent/router.py
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

BRANCH_ALIASES = {
    "B1": "CONUT JNAH",
    "B2": "CONUT - TYRE",
    "B3": "MAIN STREET COFFEE",
}

@dataclass
class Intent:
    name: str
    params: Dict[str, Any]
    confidence: float

_BRANCH_RE = re.compile(r"\b(b\d+)\b", re.IGNORECASE)         # B1, b2...
_SHIFT_RE  = re.compile(r"\bshift\s*([a-z])\b", re.IGNORECASE) # shift A
_DATE_RE   = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")            # 2026-03-01

def _extract_branch(text: str) -> Optional[str]:
    m = _BRANCH_RE.search(text)
    return m.group(1).upper() if m else None

def _extract_shift(text: str) -> Optional[str]:
    m = _SHIFT_RE.search(text)
    return m.group(1).upper() if m else None

def _extract_date(text: str) -> Optional[str]:
    m = _DATE_RE.search(text)
    return m.group(1) if m else None

def route_intent(user_text: str) -> Intent:
    t = user_text.lower()

    branch = _extract_branch(user_text)

    if branch:
        branch = branch.strip().upper()
        branch = BRANCH_ALIASES.get(branch, branch)

    shift = _extract_shift(user_text)
    date = _extract_date(user_text)


    # Forecast
    if any(k in t for k in ["forecast", "predict sales", "sales prediction", "demand"]):
        return Intent(
            name="forecast",
            params={"branch": branch, "date": date},
            confidence=0.85 if (branch or date) else 0.65,
        )

    # Staffing
    if any(k in t for k in ["staffing", "schedule", "shift plan", "crew", "roster"]):
        return Intent(
            name="staffing",
            params={"branch": branch, "shift": shift, "date": date},
            confidence=0.85 if (branch or shift) else 0.65,
        )

    # Combo
    if any(k in t for k in ["combo", "bundle", "best combo", "upsell", "pairing"]):
        return Intent(
            name="combo",
            params={"branch": branch},
            confidence=0.80 if branch else 0.60,
        )

    # Expansion
    if any(k in t for k in ["expansion", "new branch", "open a branch", "location", "where to expand"]):
        return Intent(
            name="expansion",
            params={},
            confidence=0.75,
        )

    # Beverage strategy
    if any(k in t for k in ["beverage", "drinks", "juice", "coffee", "menu", "strategy"]):
        return Intent(
            name="beverage_strategy",
            params={"branch": branch},
            confidence=0.75 if branch else 0.60,
        )

    # Fallback
    return Intent(name="general", params={}, confidence=0.30)