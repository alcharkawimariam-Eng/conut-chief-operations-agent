from combo import get_top_combos
from forecast import forecast_branch
from staffing import estimate_staff
from expansion import rank_expansion_candidates
from beverage_strategy import coffee_milkshake_actions

def handle_request(intent, **kwargs):
    """
    Routes requests to the correct function based on intent.
    """
    if intent == "combo":
        return get_top_combos(**kwargs)
    elif intent == "forecast":
        return forecast_branch(**kwargs)
    elif intent == "staffing":
        return estimate_staff(**kwargs)
    elif intent == "expansion":
        return rank_expansion_candidates(**kwargs)
    elif intent == "beverage_strategy":
        return coffee_milkshake_actions(**kwargs)
    else:
        return {"error": f"Unknown intent {intent}"}
