"""Option builder: every realistic next move for a customer, fully priced. Owner: Samu. Story: NM-5.

This module does NOT judge affordability or rank (that's NM-11). It only answers:
"if you did X, what would it cost you?"
"""
from engine import constants as C
from engine.finance import (
    loan_payment, lease_payment, mileage_overage_fee, monthly_fuel_cost, projected_end_miles,
)


def _usd(x: float) -> str:
    """$1,275 style (no cents) for human-readable trade-off text."""
    return f"${x:,.0f}"


def _catalog(model_id: str) -> dict:
    if model_id not in C.VEHICLE_CATALOG:
        raise ValueError(f"unknown vehicle model id: {model_id}")
    return C.VEHICLE_CATALOG[model_id]


def _option(*, kind, title, vehicle_label, keeps_vehicle, monthly_payment, current_payment,
            upfront_cost, term_months, total_cost, fuel_monthly, tradeoffs, assumptions, action,
            equity_used=0.0, target=None, effective_monthly=None) -> dict:
    """Single place that builds the option shape, so every option has every field."""
    return {
        "id": f"{kind}:{target}" if target else kind,   # unique; kind is what tests/ranking use
        "kind": kind,
        "target": target,
        "title": title,
        "vehicle_label": vehicle_label,
        "keeps_vehicle": keeps_vehicle,
        "monthly_payment": monthly_payment,
        "delta_monthly": monthly_payment - current_payment,
        "upfront_cost": upfront_cost,
        "term_months": term_months,
        "total_cost": total_cost,
        "fuel_monthly": fuel_monthly,
        # first-year monthly burden, used for ranking in NM-11
        "effective_monthly": (effective_monthly if effective_monthly is not None
                              else monthly_payment + fuel_monthly + upfront_cost / 12),
        "equity_used": equity_used,
        "tradeoffs": tradeoffs,
        "assumptions": {**assumptions, "source": "synthetic"},
        "action": action,
    }


# leases

def _lease_options(p: dict) -> list[dict]:
    v, c = p["vehicle"], p["contract"]
    current_pay = c["monthly_payment"]
    current = _catalog(v["catalog_id"])
    fuel_now = monthly_fuel_cost(p["miles_per_year"], current["mpg"], C.FUEL_PRICE)

    projected = projected_end_miles(v["mileage"], c["months_elapsed"], c["months_remaining"])
    # life event "longer_commute" (NM-17): extra miles driven over the remaining months
    projected += round(p.get("extra_miles_per_year", 0) * c["months_remaining"] / 12)
    over_miles = max(0, projected - c["miles_allowed_total"])
    overage_fee = mileage_overage_fee(projected, c["miles_allowed_total"], C.OVERAGE_RATE_PER_MILE)
    return_cost = overage_fee + C.DISPOSITION_FEE
    hidden_equity = v["est_value"] - c["residual"]
    opts = []

    # Buyout: buy the car for the residual, finance it as a used-car loan
    buy_price = c["residual"] + C.PURCHASE_OPTION_FEE
    pay = loan_payment(buy_price, C.USED_AUTO_APR, C.BUYOUT_TERM)
    tradeoffs = []
    if overage_fee > 0:
        tradeoffs.append(f"Avoids the {_usd(overage_fee)} over-mileage fee")
    if hidden_equity > 0:
        tradeoffs.append(f"You buy it for {_usd(c['residual'])}, about {_usd(hidden_equity)} below its value")
    tradeoffs.append("You own the car; repairs after warranty are on you")
    opts.append(_option(
        kind="lease_buyout", title=f"Buy out your {v['model']}", vehicle_label=current["label"],
        keeps_vehicle=True, monthly_payment=pay, current_payment=current_pay, upfront_cost=0,
        term_months=C.BUYOUT_TERM, total_cost=pay * C.BUYOUT_TERM, fuel_monthly=fuel_now,
        equity_used=max(0, hidden_equity), tradeoffs=tradeoffs,
        assumptions={"apr": C.USED_AUTO_APR, "term_months": C.BUYOUT_TERM, "residual": c["residual"],
                     "purchase_option_fee": C.PURCHASE_OPTION_FEE},
        action={"kind": "self_service", "label": "Start buyout"},
    ))

    # New lease on each target (return as-is, or prepay miles first)
    for target in p.get("vehicle_targets", []):
        t = _catalog(target)
        if not t["msrp"] or not t["lease_residual_pct"]:
            continue
        residual = t["msrp"] * t["lease_residual_pct"]
        new_pay = lease_payment(t["msrp"], residual, C.NEW_LEASE_MONEY_FACTOR, C.NEW_LEASE_TERM)
        fuel_new = monthly_fuel_cost(p["miles_per_year"], t["mpg"], C.FUEL_PRICE)
        lease_assumptions = {"msrp": t["msrp"], "residual": round(residual, 2),
                             "money_factor": C.NEW_LEASE_MONEY_FACTOR, "term_months": C.NEW_LEASE_TERM,
                             "disposition_fee": C.DISPOSITION_FEE}

        opts.append(_option(
            kind="return_new_lease", target=target, title=f"Return it and lease a {t['label']}",
            vehicle_label=t["label"], keeps_vehicle=True, monthly_payment=new_pay,
            current_payment=current_pay, upfront_cost=return_cost, term_months=C.NEW_LEASE_TERM,
            total_cost=new_pay * C.NEW_LEASE_TERM + return_cost, fuel_monthly=fuel_new,
            tradeoffs=[f"{_usd(return_cost)} due at return (mileage + disposition fees)", "Newer car, new warranty"],
            assumptions={**lease_assumptions, "overage_rate": C.OVERAGE_RATE_PER_MILE},
            action={"kind": "offer", "label": "See lease offer"},
        ))

        if over_miles > 0:
            prepaid = over_miles * C.PREPAID_MILES_RATE
            upfront = prepaid + C.DISPOSITION_FEE
            opts.append(_option(
                kind="buy_miles_new_lease", target=target,
                title=f"Prepay your extra miles and lease a {t['label']}", vehicle_label=t["label"],
                keeps_vehicle=True, monthly_payment=new_pay, current_payment=current_pay,
                upfront_cost=upfront, term_months=C.NEW_LEASE_TERM,
                total_cost=new_pay * C.NEW_LEASE_TERM + upfront, fuel_monthly=fuel_new,
                tradeoffs=[f"Prepaid miles cost {_usd(prepaid)} instead of a {_usd(overage_fee)} fee",
                           f"{_usd(upfront)} due upfront"],
                assumptions={**lease_assumptions, "prepaid_miles_rate": C.PREPAID_MILES_RATE,
                             "extra_miles": over_miles},
                action={"kind": "offer", "label": "See lease offer"},
            ))

    # 4. Walk away: return the car, pay the fees, no car afterwards
    walk_tradeoffs = ["No car payment", "You'll need another way to get around"]
    if hidden_equity > 0:
        walk_tradeoffs.insert(1, f"You give up about {_usd(hidden_equity)} in equity")
    opts.append(_option(
        kind="return_walk_away", title="Return the car and walk away", vehicle_label=current["label"],
        keeps_vehicle=False, monthly_payment=0, current_payment=current_pay, upfront_cost=return_cost,
        term_months=0, total_cost=return_cost, fuel_monthly=0, tradeoffs=walk_tradeoffs,
        assumptions={"overage_rate": C.OVERAGE_RATE_PER_MILE, "disposition_fee": C.DISPOSITION_FEE,
                     "projected_miles": projected},
        action={"kind": "follow_up", "label": "Talk to a TFS specialist"},
    ))
    return opts


# loans

def _loan_options(p: dict, include_relief: bool) -> list[dict]:
    v, c = p["vehicle"], p["contract"]
    pay_now, apr, months_left, payoff = c["monthly_payment"], c["apr"], c["months_remaining"], c["payoff"]
    current = _catalog(v["catalog_id"])
    fuel_now = monthly_fuel_cost(p["miles_per_year"], current["mpg"], C.FUEL_PRICE)
    car_equity = v["est_value"] - payoff
    opts = []

    # Keep: change nothing (the baseline every other option is compared to)
    opts.append(_option(
        kind="keep", title=f"Keep your {v['model']} as is", vehicle_label=current["label"],
        keeps_vehicle=True, monthly_payment=pay_now, current_payment=pay_now, upfront_cost=0,
        term_months=months_left, total_cost=pay_now * months_left, fuel_monthly=fuel_now,
        tradeoffs=[f"Paid off in {months_left} months", "No paperwork, no new commitments"],
        assumptions={"apr": apr, "term_months": months_left},
        action={"kind": "self_service", "label": "Set up payment reminders"},
    ))

    # Refinance: only if today's rate beats theirs
    if apr > C.REFI_APR:
        pay = loan_payment(payoff, C.REFI_APR, months_left)
        saved = pay_now * months_left - pay * months_left
        opts.append(_option(
            kind="refinance", title=f"Refinance at {C.REFI_APR}%", vehicle_label=current["label"],
            keeps_vehicle=True, monthly_payment=pay, current_payment=pay_now, upfront_cost=0,
            term_months=months_left, total_cost=pay * months_left, fuel_monthly=fuel_now,
            tradeoffs=[f"Saves about {_usd(saved)} over the rest of the loan", "Same car, same payoff date"],
            assumptions={"apr": C.REFI_APR, "previous_apr": apr, "term_months": months_left, "payoff": payoff},
            action={"kind": "self_service", "label": "Check refinance offer"},
        ))

    # Trade-in/upgrade: equity becomes the down payment on a new car
    for target in dict.fromkeys(p.get("vehicle_targets", [])):   # dedupe, keep order
        t = _catalog(target)
        if not t["msrp"]:
            continue
        financed = t["msrp"] - car_equity                       # negative equity rolls in
        pay = loan_payment(financed, C.NEW_AUTO_APR, C.NEW_TERM)
        fuel_new = monthly_fuel_cost(p["miles_per_year"], t["mpg"], C.FUEL_PRICE)
        tradeoffs = [f"Uses your {_usd(car_equity)} equity as a down payment" if car_equity >= 0
                     else f"Rolls {_usd(-car_equity)} of negative equity into the new loan"]
        if fuel_new < fuel_now:
            tradeoffs.append(f"About {_usd(fuel_now - fuel_new)}/mo less on gas")
        elif fuel_new > fuel_now:
            tradeoffs.append(f"About {_usd(fuel_new - fuel_now)}/mo more on gas")
        tradeoffs.append(f"New {C.NEW_TERM}-month loan")
        opts.append(_option(
            kind="trade_in_upgrade", target=target, title=f"Trade in for a {t['label']}",
            vehicle_label=t["label"], keeps_vehicle=True, monthly_payment=pay, current_payment=pay_now,
            upfront_cost=0, term_months=C.NEW_TERM, total_cost=pay * C.NEW_TERM, fuel_monthly=fuel_new,
            equity_used=car_equity, tradeoffs=tradeoffs,
            assumptions={"msrp": t["msrp"], "trade_in_value": v["est_value"], "payoff": payoff,
                         "apr": C.NEW_AUTO_APR, "term_months": C.NEW_TERM},
            action={"kind": "offer", "label": "See upgrade offer"},
        ))

    # Relief options: only when NM-11 says the customer is short every month
    if include_relief:
        term = months_left + C.EXTENSION_MONTHS
        pay = loan_payment(payoff, apr, term)
        extra_total = pay * term - pay_now * months_left
        opts.append(_option(
            kind="extend_term", title=f"Extend your loan by {C.EXTENSION_MONTHS} months",
            vehicle_label=current["label"], keeps_vehicle=True, monthly_payment=pay, current_payment=pay_now,
            upfront_cost=0, term_months=term, total_cost=pay * term, fuel_monthly=fuel_now,
            tradeoffs=[f"Lowers your payment by {_usd(pay_now - pay)}/mo",
                       f"Costs about {_usd(extra_total)} more in total"],
            assumptions={"apr": apr, "term_months": term, "extension_months": C.EXTENSION_MONTHS},
            action={"kind": "self_service", "label": "Request extension"},
        ))

        r = apr / 1200
        accrued = payoff * ((1 + r) ** C.DEFERRAL_MONTHS - 1)    # interest that builds while skipping
        opts.append(_option(
            kind="payment_deferral", title=f"Skip your next {C.DEFERRAL_MONTHS} payments",
            vehicle_label=current["label"], keeps_vehicle=True, monthly_payment=0, current_payment=pay_now,
            upfront_cost=0, term_months=months_left + C.DEFERRAL_MONTHS,
            total_cost=pay_now * months_left + accrued, fuel_monthly=fuel_now,
            tradeoffs=[f"No payment for {C.DEFERRAL_MONTHS} months",
                       f"About {_usd(accrued)} in extra interest; payments move to the end"],
            assumptions={"apr": apr, "deferral_months": C.DEFERRAL_MONTHS},
            action={"kind": "follow_up", "label": "Request deferral"},
            # a $0 payment only lasts 2 months, so average the first year instead
            effective_monthly=(pay_now * (12 - C.DEFERRAL_MONTHS) + accrued) / 12 + fuel_now,
        ))
    return opts


# public

def build_options(profile: dict, include_relief: bool = False) -> list[dict]:
    """Every candidate option for this profile, each fully priced (unranked, unfiltered)."""
    contract_type = profile["contract"]["type"]
    if contract_type == "lease":
        return _lease_options(profile)
    if contract_type == "loan":
        return _loan_options(profile, include_relief)
    raise ValueError(f"unknown contract type: {contract_type}")