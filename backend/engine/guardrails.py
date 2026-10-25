"""Affordability rules and deterministic ranking.

This is the responsible-AI core: the ENGINE (not the LLM) decides what a customer can afford
and what ranks first, and every rejection carries a human-readable reason.
"""
from engine import constants as C

# Which option kinds satisfy which customer goal
GOAL_MATCHES = {
    "newer_vehicle": {"trade_in_upgrade", "return_new_lease", "buy_miles_new_lease"},
    "lower_payment": {"refinance", "extend_term"},
    "more_space": {"trade_in_upgrade"},
    "no_car_needed": {"return_walk_away"},
}


def _usd(x: float) -> str:
    return f"${x:,.0f}"


def check_affordability(option: dict, finances: dict) -> tuple[bool, str | None]:
    """Apply the 3 rules in order. Returns (affordable, reason_of_first_failed_rule)."""
    income = finances["monthly_income"]
    surplus = finances["monthly_surplus"]
    bills = finances["monthly_bills"]
    savings = finances["savings"]
    raises_payment = option["delta_monthly"] > 0

    # Rule 1: car payment <= 15% of income (only for options that raise the payment)
    if raises_payment:
        limit = C.PAYMENT_TO_INCOME_MAX * income
        if option["monthly_payment"] > limit:
            pct = option["monthly_payment"] / income * 100 if income > 0 else float("inf")
            return False, (f"Payment would be {pct:.0f}% of your income "
                           f"(limit {C.PAYMENT_TO_INCOME_MAX:.0%})")

    # Rule 2: payment increase <= 50% of monthly surplus
    if raises_payment:
        limit = C.SURPLUS_SHARE_MAX * surplus
        if option["delta_monthly"] > limit:
            if surplus <= 0:
                return False, f"Adds {_usd(option['delta_monthly'])}/mo, but you have no monthly surplus"
            return False, (f"Adds {_usd(option['delta_monthly'])}/mo; your monthly surplus is "
                           f"{_usd(surplus)} (limit {_usd(limit)})")

    # Rule 3: after upfront costs, keep at least 1 month of bills in savings
    if option["upfront_cost"] > 0:
        left = savings - option["upfront_cost"]
        if left < C.MIN_BUFFER_MONTHS * bills:
            return False, (f"Upfront cost of {_usd(option['upfront_cost'])} would leave {_usd(left)} "
                           f"in savings, less than one month of bills ({_usd(bills)})")

    return True, None


def is_relief_needed(finances: dict) -> bool:
    """Customer is short every month -> offer extension/deferral + human handoff."""
    return finances["monthly_surplus"] < C.RELIEF_SURPLUS_MIN


def _matches_goal(option: dict, goals: list[str]) -> bool:
    return any(option["kind"] in GOAL_MATCHES.get(g, set()) for g in goals)


def rank_options(options: list[dict], goals: list[str]) -> list[dict]:
    """Deterministic order. Options must already carry 'affordable'.

    1. affordable first
    2. options that leave you without a car go last (unless the goal is no_car_needed)
    3. options matching a customer goal first
    4. lowest effective monthly cost (payment + fuel + upfront/12)
    5. tie-break: lowest total cost
    """
    def key(o):
        no_car_penalty = (not o["keeps_vehicle"]) and "no_car_needed" not in goals
        return (
            not o["affordable"],
            no_car_penalty,
            not _matches_goal(o, goals),
            o["effective_monthly"],
            o["total_cost"],
        )
    return sorted(options, key=key)