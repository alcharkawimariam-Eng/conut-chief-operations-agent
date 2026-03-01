# src/ops_agent/formatter.py
from typing import Any, Dict, List
from .router import Intent


def _fmt_number(x: Any) -> str:
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return str(x)


def _fmt_pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.0f}%"
    except Exception:
        return str(x)


def format_exec_answer(intent: Intent, result: Dict[str, Any]) -> str:
    """
    Turns model output dict -> executive-style message.
    Supports both rich dicts and simple outputs.
    """

    # If runner returns a simple fallback
    if result.get("type") == "general":
        return result.get("message", "How can I help with operations today?")

    title_map = {
        "forecast": "Sales Forecast",
        "staffing": "Staffing Plan",
        "combo": "Combo Optimization",
        "expansion": "Expansion Recommendation",
        "beverage_strategy": "Beverage Strategy",
    }
    title = title_map.get(intent.name, "Operations Insight")

    conf = result.get("confidence", intent.confidence)

    # ✅ Special formatting for Forecast model output
    if intent.name == "forecast":
        branch = result.get("branch", (intent.params or {}).get("branch") or "UNKNOWN")
        metric = result.get("target_metric", "Total_Revenue")
        horizon = result.get("horizon_days", len(result.get("forecast", []) or []))
        method = result.get("method", "model")

        hist = result.get("historical_summary") or {}
        last_date = hist.get("last_observed_date")
        last_val = hist.get("last_observed_value")

        forecast_rows: List[Dict[str, Any]] = result.get("forecast") or []
        show_rows = forecast_rows[: min(7, len(forecast_rows))]

        lines = [f"**{title} — {branch}**"]
        lines.append(f"- Metric: {metric}")
        lines.append(f"- Horizon: {horizon} days")
        lines.append(f"- Method: {method}")

        if last_date and last_val is not None:
            lines.append(f"- Last observed ({last_date}): {_fmt_number(last_val)}")

        if "mean" in hist and hist.get("mean") is not None:
            lines.append(f"- Historical mean: {_fmt_number(hist['mean'])}")

        lines.append("")
        lines.append("**Next days**")
        for r in show_rows:
            d = r.get("date")
            v = r.get("predicted_value")
            lines.append(f"• {d}: {_fmt_number(v)}")

        if conf is not None:
            lines.append("")
            lines.append(f"**Confidence:** {_fmt_pct(conf)}")

        return "\n".join(lines)

    # Optional structured fields (for other models later)
    kpis = result.get("kpis") or {}
    recs = result.get("recommendations") or []
    notes = result.get("notes")

    # If model returned plain text or plain value
    if not kpis and not recs and not notes:
        if "text" in result:
            msg = f"**{title}**\n\n{result['text']}"
        else:
            msg = f"**{title}**\n\n{result}"
        if conf is not None:
            msg += f"\n\nConfidence: {_fmt_pct(conf)}"
        return msg

    lines = [f"**{title}**"]

    # Show scope (branch/shift/date) if present
    scope = {k: v for k, v in (intent.params or {}).items() if v}
    if scope:
        lines.append(f"Scope: {scope}")

    if kpis:
        lines.append("\n**Key KPIs**")
        for k, v in kpis.items():
            lines.append(f"- {k}: {v}")

    if recs:
        lines.append("\n**Operational Recommendations**")
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {r}")

    if conf is not None:
        lines.append(f"\nConfidence: {_fmt_pct(conf)}")

    if notes:
        lines.append(f"\nNotes: {notes}")

    return "\n".join(lines)