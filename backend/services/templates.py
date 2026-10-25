"""Deterministic fallback explanations. Owner: Jose. Story: NM-14."""


def format_money(n: float) -> str:
    """$1,160 for whole amounts, $294.34 otherwise (same as the frontend's formatCurrency)."""
    n = round(n, 2)
    if n == int(n):
        return f"${int(n):,}"
    return f"${n:,.2f}"


def template_explanation(option: dict) -> str:
    """'{title}: ${monthly}/mo for {term} months. {tradeoff}. {action}.' using only the option's own fields."""
    head = f"{option['title']}: {format_money(option['monthly_payment'])}/mo"
    if option.get("term_months"):
        head += f" for {option['term_months']} months"
    parts = [head + "."]

    tradeoffs = option.get("tradeoffs") or []
    if tradeoffs:
        parts.append(tradeoffs[0].rstrip(".") + ".")

    label = (option.get("action") or {}).get("label")
    if label:
        parts.append(label.rstrip(".") + ".")
    return " ".join(parts)
