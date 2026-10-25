"""End-to-end persona checks: real data + real engine = the demo story. Owner: Rodrigo + Samu. Story: NM-18."""
import pytest

from engine.recommend import recommend
from services.customer_profile import build_profile

# The 8 scenarios from Appendix B "Expected outcomes": (customer, life event, expected #1 option)
SCENARIOS = [
    ("p1", None, "lease_buyout"),
    ("p1", {"type": "longer_commute", "params": {}}, "lease_buyout"),
    ("p2", None, "keep"),
    ("p2", {"type": "new_baby", "params": {}}, "keep"),
    ("p2", {"type": "income_drop", "params": {"pct": 20}}, "talk_to_advisor"),
    ("p3", None, "trade_in_upgrade"),
    ("p3", {"type": "income_drop", "params": {"pct": 20}}, "trade_in_upgrade"),
    ("p3", {"type": "longer_commute", "params": {}}, "trade_in_upgrade"),
]


def top_kinds(customer_id, life_event=None):
    """Runs the full pipeline and returns the kinds of the recommended cards, in order."""
    result = recommend(build_profile(customer_id), life_event)
    return [card["kind"] for card in result["recommendations"]]


@pytest.mark.parametrize("customer_id, life_event, expected_first", SCENARIOS)
def test_best_move_matches_demo_script(customer_id, life_event, expected_first):
    kinds = top_kinds(customer_id, life_event)
    event_name = life_event["type"] if life_event else "baseline"
    assert kinds[0] == expected_first, f"{customer_id} + {event_name}: got {kinds}"


def test_maya_gets_buy_miles_as_second_option():
    assert top_kinds("p1")[:2] == ["lease_buyout", "buy_miles_new_lease"]


def test_reyes_highlander_becomes_unaffordable_after_baby():
    result = recommend(build_profile("p2"), {"type": "new_baby", "params": {}})
    highlander = next(card for card in result["considered"] if card["kind"] == "trade_in_upgrade")
    assert highlander["affordable"] is False
    assert highlander["rejection_reason"]