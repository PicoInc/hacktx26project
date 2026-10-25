"""Pure finance functions: loan/lease payments, balance, mileage, equity, fuel. Owner: Samu. Story: NM-4.
The file verifies and applies math to the input provided by the frontend. No math is done by an LLM
but by the following functions.

Rules: no I/O, no rounding (the API rounds once at the boundary), ValueError on bad input.
"""


def _monthly_rate(apr_pct: float) -> float:
    """APR in percent (e.g. 4.9) -> monthly decimal rate (0.004083...)."""
    if apr_pct < 0:
        raise ValueError("apr_pct must be >= 0")
    return apr_pct / 1200

def loan_payment(principal: float, apr_pct: float, term_months: int) -> float:
    """Fixed monthly payment for an amortized loan: P = PV*r / (1 - (1+r)^-n)."""
    if term_months <= 0:
        raise ValueError("term_months must be > 0")
    if principal < 0:
        raise ValueError("principal must be >= 0")
    r = _monthly_rate(apr_pct)
    if r == 0:
        return principal / term_months
    return principal * r / (1 - (1 + r) ** -term_months)

# Loans 

def loan_balance(principal: float, apr_pct: float, term_months: int, payments_made: int) -> float:
    """Remaining principal (payoff) after `payments_made` payments: B = PV(1+r)^k - P((1+r)^k - 1)/r."""
    if payments_made < 0:
        raise ValueError("payments_made must be >= 0")
    if payments_made >= term_months:
        return 0.0
    payment = loan_payment(principal, apr_pct, term_months)
    r = _monthly_rate(apr_pct)
    k = payments_made
    if r == 0:
        return max(0.0, principal - payment * k)
    growth = (1 + r) ** k
    return max(0.0, principal * growth - payment * (growth - 1) / r)


# Leases

def lease_payment(cap_cost: float, residual: float, money_factor: float, term_months: int) -> float:
    """Monthly lease payment = depreciation fee + finance charge."""
    if term_months <= 0:
        raise ValueError("term_months must be > 0")
    if cap_cost < 0 or residual < 0 or money_factor < 0:
        raise ValueError("cap_cost, residual and money_factor must be >= 0")
    if residual > cap_cost:
        raise ValueError("residual cannot exceed cap_cost")
    depreciation_fee = (cap_cost - residual) / term_months
    finance_charge = (cap_cost + residual) * money_factor
    return depreciation_fee + finance_charge


def apr_to_money_factor(apr_pct: float) -> float:
    """Lease money factor from APR: MF = APR / 2400."""
    if apr_pct < 0:
        raise ValueError("apr_pct must be >= 0")
    return apr_pct / 2400


# Mileage

def projected_end_miles(current_miles: int, months_elapsed: int, months_remaining: int) -> int:
    """Miles at lease end if the customer keeps their current pace."""
    if months_elapsed <= 0:
        raise ValueError("months_elapsed must be > 0")
    if current_miles < 0 or months_remaining < 0:
        raise ValueError("current_miles and months_remaining must be >= 0")
    pace_per_month = current_miles / months_elapsed
    return round(current_miles + pace_per_month * months_remaining)


def mileage_overage_fee(projected_miles: int, allowed_miles: int, rate_per_mile: float) -> float:
    """Fee for returning a lease over its mileage allowance. Never negative."""
    if rate_per_mile < 0:
        raise ValueError("rate_per_mile must be >= 0")
    return max(0, projected_miles - allowed_miles) * rate_per_mile


# Equiry and running costs 

def equity(market_value: float, payoff: float) -> float:
    """Car value minus what's still owed. Negative = underwater."""
    return market_value - payoff


def monthly_fuel_cost(miles_per_year: int, mpg: float, fuel_price: float) -> float:
    """Average monthly fuel spend."""
    if mpg <= 0:
        raise ValueError("mpg must be > 0")
    if miles_per_year < 0 or fuel_price < 0:
        raise ValueError("miles_per_year and fuel_price must be >= 0")
    return miles_per_year / mpg * fuel_price / 12