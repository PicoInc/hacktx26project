"""Pure finance functions: loan/lease payments, balance, mileage, equity, fuel. Owner: Samu. Story: NM-4."""


def loan_payment(principal: float, apr_pct: float, term_months: int) -> float:
    raise NotImplementedError


def loan_balance(principal: float, apr_pct: float, term_months: int, payments_made: int) -> float:
    raise NotImplementedError


def lease_payment(cap_cost: float, residual: float, money_factor: float, term_months: int) -> float:
    raise NotImplementedError
