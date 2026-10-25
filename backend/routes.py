"""API routes. Owner: Rodrigo. Contract: docs/contract.md"""
from flask import Blueprint, jsonify, request

from engine.finance import equity
from engine.recommend import recommend
from services.customer_profile import build_profile, list_personas
from services.llm import explain_all

api = Blueprint("api", __name__)

# Life events the "What if?" panel can send (from docs/contract.md)
ALLOWED_LIFE_EVENTS = ["new_baby", "income_drop", "longer_commute"]
MONEY_DECIMALS = 2


# Decimals that are NOT money and must keep their precision
NOT_MONEY_KEYS = {"money_factor"}


def round_money(value, key=None):
    """Rounds every money number inside a dict or list to 2 decimals (cents)."""
    if key in NOT_MONEY_KEYS:
        return value
    if isinstance(value, float):
        return round(value, MONEY_DECIMALS)
    if isinstance(value, dict):
        return {item_key: round_money(item, item_key) for item_key, item in value.items()}
    if isinstance(value, list):
        return [round_money(item, key) for item in value]
    return value


def read_life_event():
    """Gets the life event from the request body. Returns (life_event, error_message)."""
    body = request.get_json(silent=True) or {}
    life_event = body.get("life_event")

    if life_event is None:
        return None, None
    if not isinstance(life_event, dict) or life_event.get("type") not in ALLOWED_LIFE_EVENTS:
        return None, "invalid life event type"

    life_event.setdefault("params", {})
    return life_event, None


@api.get("/personas")
def get_personas():
    """List of customers for the persona picker."""
    return jsonify(list_personas())


@api.get("/customers/<customer_id>/dashboard")
def get_dashboard(customer_id):
    """Full dashboard for one customer: profile + equity."""
    profile = build_profile(customer_id)

    equity_value = round(equity(profile["vehicle"]["est_value"], profile["contract"]["payoff"]), 2)
    equity_status = "positive" if equity_value >= 0 else "negative"

    dashboard = {
        **profile,
        "equity": {"value": equity_value, "status": equity_status},
        "equity_timeline": [],
    }
    return jsonify(dashboard)


@api.post("/customers/<customer_id>/recommendations")
def get_recommendations(customer_id):
    """Ranked recommendations (engine) with plain-English explanations (AI)."""
    life_event, error_message = read_life_event()
    if error_message:
        return jsonify(error=error_message, allowed=ALLOWED_LIFE_EVENTS), 400

    profile = build_profile(customer_id)
    result = recommend(profile, life_event)

    explanations = explain_all(result["recommendations"], profile, life_event)
    for recommendation in result["recommendations"]:
        explanation = explanations.get(recommendation["id"], {})
        recommendation["explanation"] = explanation.get("text", "")
        recommendation["explanation_source"] = explanation.get("source", "template")

    return jsonify(round_money(result))