"""Equity timeline for the chart. Owner: Rodrigo. Story: NM-23."""
from engine.constants import DEPRECIATION_PER_YEAR
from engine.finance import loan_balance

MONTHS_PER_YEAR = 12
DEFAULT_TIMELINE_MONTHS = 24


def estimated_value(value_today, months_from_now):
    """Car value after some months, losing DEPRECIATION_PER_YEAR of its value each year."""
    years_from_now = months_from_now / MONTHS_PER_YEAR
    return value_today * (1 - DEPRECIATION_PER_YEAR) ** years_from_now


def payoff_after(contract, months_from_now):
    """What the customer still owes after some more months of payments."""
    if contract["type"] == "lease":
        return contract["residual"]
    remaining = loan_balance(contract["payoff"], contract["apr"],
                             contract["months_remaining"], months_from_now)
    return max(0, remaining)


def equity_timeline(profile, months=DEFAULT_TIMELINE_MONTHS):
    """Month-by-month car value vs. payoff, from today until `months` or the contract end."""
    contract = profile["contract"]
    value_today = profile["vehicle"]["est_value"]
    last_month = min(months, contract["months_remaining"])

    timeline = []
    for month in range(last_month + 1):
        timeline.append({
            "month": month,
            "value": round(estimated_value(value_today, month), 2),
            "payoff": round(payoff_after(contract, month), 2),
        })
    return timeline