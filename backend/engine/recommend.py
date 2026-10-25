"""The ONLY engine function the API calls. 

profile (+ optional life event) -> priced options -> affordability -> ranking -> top 3.
"""
import copy

from engine import constants as C
from engine.guardrails import check_affordability, is_relief_needed, rank_options
from engine.options import build_options, _option

TOP_N = 3


def _advisor_card(profile: dict) -> dict:
    """Human handoff, pinned to #1 when the customer is short every month or nothing is affordable."""
    pay_now = profile["contract"]["monthly_payment"]
    months = profile["contract"].get("months_remaining", 0)
    card = _option(
        kind="talk_to_advisor", title="Talk to a TFS specialist first",
        vehicle_label="", keeps_vehicle=True, monthly_payment=pay_now, current_payment=pay_now,
        upfront_cost=0, term_months=months,
        # Nothing changes until the customer talks to someone, so the cost is today's plan
        total_cost=pay_now * months, fuel_monthly=0,
        tradeoffs=["Your monthly budget is tight right now",
                   "A specialist can review relief options with you"],
        assumptions={}, action={"kind": "follow_up", "label": "Schedule a call"},
        effective_monthly=0,
    )
    card.update(affordable=True, rejection_reason=None)
    return card


def _evaluate(profile: dict) -> dict:
    """Core pipeline for one profile (no life-event handling)."""
    finances = profile["finances"]
    relief = is_relief_needed(finances)

    options = build_options(profile, include_relief=relief)
    for o in options:
        o["affordable"], o["rejection_reason"] = check_affordability(o, finances)

    ranked = rank_options(options, profile.get("goals", []))
    affordable = [o for o in ranked if o["affordable"]]

    if relief or not affordable:
        ranked = [_advisor_card(profile)] + ranked
        affordable = [ranked[0]] + affordable

    for i, o in enumerate(affordable, start=1):
        o["rank"] = i
    for o in ranked:
        o.setdefault("rank", None)       # rejected options have no rank

    return {
        "recommendations": affordable[:TOP_N],
        "considered": ranked,
        "relief_needed": relief,
    }


def recommend(profile: dict, life_event: dict | None = None) -> dict:
    """Returns { recommendations, considered, relief_needed, life_event_applied, finances_after_event }.

    Never mutates `profile`. Money is NOT rounded here (the API rounds once at the boundary).
    """
    profile = copy.deepcopy(profile)
    if life_event is None:
        result = _evaluate(profile)
        result.update(life_event_applied=None, finances_after_event=None)
        for o in result["considered"]:
            o["previous_rank"] = None
        return result

    # Life events (NM-17): rank before vs after so the UI can show "↑ was #2"
    from engine.events import apply_life_event, describe_life_event
    baseline = _evaluate(copy.deepcopy(profile))
    before_ranks = {o["id"]: o["rank"] for o in baseline["considered"]}

    changed = apply_life_event(profile, life_event)
    result = _evaluate(changed)
    for o in result["considered"]:
        o["previous_rank"] = before_ranks.get(o["id"])
    result.update(
        life_event_applied=describe_life_event(profile, changed, life_event),
        finances_after_event=changed["finances"],
    )
    return result