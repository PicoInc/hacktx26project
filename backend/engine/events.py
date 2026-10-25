"""Life events for the What-if simulator. Owner: Samu. Story: NM-17.

A life event changes the customer's SITUATION (income, spending, miles, goals) before the engine runs.
It never touches prices or rules, so every recommendation still comes from the same tested pipeline.
"""
import copy

from engine.finance import monthly_fuel_cost, projected_end_miles
from engine import constants as C

# Rodrigo's route imports this for its 400 check, so API and engine never drift apart
ALLOWED_EVENTS = ("new_baby", "income_drop", "longer_commute")

DEFAULT_PARAMS = {
    "new_baby": {"monthly_cost": 500, "bigger_vehicle": "highlander_xle_2027"},
    "income_drop": {"pct": 20},
    "longer_commute": {"extra_miles_per_year": 6000},
}


def _usd(x: float) -> str:
    sign = "−" if x < 0 else ""
    return f"{sign}${abs(x):,.0f}"


def _recompute_surplus(f: dict) -> None:
    f["monthly_surplus"] = f["monthly_income"] - f["monthly_bills"] - f["monthly_spending"]


def _params(event: dict) -> dict:
    """Validate the event and merge its params over the defaults."""
    if not isinstance(event, dict) or event.get("type") not in ALLOWED_EVENTS:
        raise ValueError(f"unknown life event; allowed: {', '.join(ALLOWED_EVENTS)}")
    params = {**DEFAULT_PARAMS[event["type"]], **(event.get("params") or {})}

    if event["type"] == "income_drop" and not 0 < params["pct"] < 100:
        raise ValueError("income_drop pct must be between 0 and 100")
    if event["type"] == "new_baby" and params["monthly_cost"] < 0:
        raise ValueError("new_baby monthly_cost must be >= 0")
    if event["type"] == "longer_commute" and params["extra_miles_per_year"] < 0:
        raise ValueError("longer_commute extra_miles_per_year must be >= 0")
    return params


def apply_life_event(profile: dict, event: dict) -> dict:
    """Return a NEW profile with the event applied. The input is never mutated."""
    params = _params(event)
    p = copy.deepcopy(profile)
    f = p["finances"]

    if event["type"] == "income_drop":
        f["monthly_income"] = f["monthly_income"] * (1 - params["pct"] / 100)

    elif event["type"] == "new_baby":
        f["monthly_spending"] = f["monthly_spending"] + params["monthly_cost"]
        p["goals"] = list(dict.fromkeys([*p.get("goals", []), "more_space"]))
        target = params["bigger_vehicle"]
        if target and target != p["vehicle"].get("catalog_id"):
            p["vehicle_targets"] = list(dict.fromkeys([*p.get("vehicle_targets", []), target]))

    elif event["type"] == "longer_commute":
        extra = params["extra_miles_per_year"]
        p["miles_per_year"] = p["miles_per_year"] + extra
        p["extra_miles_per_year"] = p.get("extra_miles_per_year", 0) + extra   # read by lease options

    _recompute_surplus(f)
    return p


def describe_life_event(before: dict, after: dict, event: dict) -> str:
    """One human line for the What-if banner, e.g. 'Income down 20% → monthly surplus now −$340'."""
    params = _params(event)
    surplus = after["finances"]["monthly_surplus"]

    if event["type"] == "income_drop":
        return f"Income down {params['pct']:g}% → monthly surplus now {_usd(surplus)}"

    if event["type"] == "new_baby":
        return (f"Baby on the way (+{_usd(params['monthly_cost'])}/mo) → "
                f"monthly surplus now {_usd(surplus)}")

    # longer_commute
    extra = params["extra_miles_per_year"]
    c = after["contract"]
    if c["type"] == "lease":
        projected = projected_end_miles(after["vehicle"]["mileage"], c["months_elapsed"], c["months_remaining"])
        projected += round(after.get("extra_miles_per_year", 0) * c["months_remaining"] / 12)
        over = max(0, projected - c["miles_allowed_total"])
        return f"Longer commute (+{extra:,} mi/yr) → projected {over:,} miles over your lease"
    mpg = C.VEHICLE_CATALOG[after["vehicle"]["catalog_id"]]["mpg"]
    gas_up = (monthly_fuel_cost(after["miles_per_year"], mpg, C.FUEL_PRICE)
              - monthly_fuel_cost(before["miles_per_year"], mpg, C.FUEL_PRICE))
    return f"Longer commute (+{extra:,} mi/yr) → about {_usd(gas_up)}/mo more on gas"