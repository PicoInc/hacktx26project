"""API routes. Owner: Rodrigo. Contract: docs/contract.md"""
from flask import Blueprint, jsonify

from engine.finance import equity
from services.customer_profile import build_profile, list_personas

api = Blueprint("api", __name__)


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


# NM-12: POST /customers/<id>/recommendations → engine.recommend.recommend() + services.llm.explain_all()