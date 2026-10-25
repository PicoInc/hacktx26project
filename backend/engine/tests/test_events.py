import copy
import pytest
from engine.events import ALLOWED_EVENTS, apply_life_event, describe_life_event
from engine.recommend import recommend
from engine.tests.fixtures import P1, P2, P3

BABY = {"type": "new_baby", "params": {}}
DROP = {"type": "income_drop", "params": {"pct": 20}}
COMMUTE = {"type": "longer_commute", "params": {}}


def kinds(options):
    return [o["kind"] for o in options]


def by_kind(options):
    return {o["kind"]: o for o in options}


# ---------- apply_life_event ----------

def test_income_drop_changes_income_and_surplus():
    p = apply_life_event(P2, DROP)
    assert p["finances"]["monthly_income"] == pytest.approx(4960)
    assert p["finances"]["monthly_surplus"] == pytest.approx(-340)


def test_new_baby_adds_cost_goal_and_bigger_vehicle():
    p = apply_life_event(P2, BABY)
    assert p["finances"]["monthly_spending"] == 2200
    assert p["finances"]["monthly_surplus"] == 400
    assert "more_space" in p["goals"]
    assert p["vehicle_targets"].count("highlander_xle_2027") == 1        # no duplicates


def test_longer_commute_adds_miles():
    p = apply_life_event(P1, COMMUTE)
    assert p["miles_per_year"] == P1["miles_per_year"] + 6000
    assert p["extra_miles_per_year"] == 6000


def test_input_never_mutated():
    before = copy.deepcopy(P2)
    apply_life_event(P2, BABY)
    apply_life_event(P2, DROP)
    assert P2 == before


def test_invalid_events():
    with pytest.raises(ValueError):
        apply_life_event(P1, {"type": "lottery_win"})
    with pytest.raises(ValueError):
        apply_life_event(P1, {"type": "income_drop", "params": {"pct": 150}})
    assert set(ALLOWED_EVENTS) == {"new_baby", "income_drop", "longer_commute"}


def test_describe():
    assert describe_life_event(P2, apply_life_event(P2, DROP), DROP) == "Income down 20% → monthly surplus now −$340"
    assert "surplus now $400" in describe_life_event(P2, apply_life_event(P2, BABY), BABY)
    assert "7,100 miles over" in describe_life_event(P1, apply_life_event(P1, COMMUTE), COMMUTE)
    assert "more on gas" in describe_life_event(P3, apply_life_event(P3, COMMUTE), COMMUTE)


# ---------- expected outcomes (Appendix B) through recommend() ----------

def test_p2_new_baby_rejects_highlander():
    r = recommend(P2, BABY)
    assert kinds(r["recommendations"]) == ["keep"]
    hl = by_kind(r["considered"])["trade_in_upgrade"]
    assert hl["affordable"] is False and "surplus is $400 (limit $200)" in hl["rejection_reason"]
    assert hl["previous_rank"] == 2                                     # it WAS #2 before the baby
    assert r["finances_after_event"]["monthly_surplus"] == 400
    assert r["life_event_applied"].startswith("Baby on the way")


def test_p2_income_drop_hands_off_with_relief():
    r = recommend(P2, DROP)
    assert r["relief_needed"] is True
    assert kinds(r["recommendations"]) == ["talk_to_advisor", "extend_term", "payment_deferral"]
    assert by_kind(r["considered"])["extend_term"]["monthly_payment"] == pytest.approx(439.52, abs=0.5)
    assert by_kind(r["considered"])["extend_term"]["previous_rank"] is None     # new option


def test_p1_longer_commute_buyout_stays_first():
    r = recommend(P1, COMMUTE)
    assert kinds(r["recommendations"])[0] == "lease_buyout"
    miles = by_kind(r["considered"])["buy_miles_new_lease"]
    assert miles["upfront_cost"] == pytest.approx(1460)                  # 7,100 mi × $0.15 + $395
    assert miles["affordable"] is False                                 # $1,140 left < $1,150 bills


def test_p3_stays_resilient():
    for event in (DROP, COMMUTE):
        assert kinds(recommend(P3, event)["recommendations"])[0] == "trade_in_upgrade"


def test_baseline_unchanged_by_event_runs():
    before = copy.deepcopy(recommend(P2))
    recommend(P2, BABY)
    assert recommend(P2) == before