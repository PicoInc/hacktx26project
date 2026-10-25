import copy
import pytest
from engine.guardrails import check_affordability, rank_options, is_relief_needed
from engine.recommend import recommend
from engine.tests.fixtures import P1, P2, P3

FIN = {"monthly_income": 6000, "monthly_bills": 3000, "monthly_spending": 2000,
       "monthly_surplus": 1000, "savings": 5000}


def opt(**kw):
    base = {"kind": "x", "monthly_payment": 500, "delta_monthly": 100, "upfront_cost": 0,
            "keeps_vehicle": True, "effective_monthly": 500, "total_cost": 10000}
    return {**base, **kw}


def kinds(options):
    return [o["kind"] for o in options]


# ---------- the 3 rules ----------

def test_rule1_payment_to_income():
    ok, reason = check_affordability(opt(monthly_payment=1000, delta_monthly=100), FIN)   # 16.7% > 15%
    assert not ok and "17% of your income" in reason


def test_rule2_surplus_share():
    ok, reason = check_affordability(opt(delta_monthly=600), FIN)                         # 600 > 500
    assert not ok and "surplus" in reason


def test_rule3_savings_buffer():
    ok, reason = check_affordability(opt(upfront_cost=2500, delta_monthly=0), FIN)        # 2500 left < 3000
    assert not ok and "one month of bills" in reason


def test_rules_skip_options_that_lower_payment():
    ok, _ = check_affordability(opt(monthly_payment=900, delta_monthly=-50), FIN)          # high, but lower than today
    assert ok


def test_no_surplus_message():
    ok, reason = check_affordability(opt(delta_monthly=50), {**FIN, "monthly_surplus": -100})
    assert not ok and "no monthly surplus" in reason


def test_relief_trigger():
    assert is_relief_needed({**FIN, "monthly_surplus": -1})
    assert not is_relief_needed(FIN)


# ---------- ranking ----------

def test_ranking_order():
    opts = [
        opt(kind="cheap_rejected", affordable=False, effective_monthly=100),
        opt(kind="no_car", affordable=True, keeps_vehicle=False, effective_monthly=50),
        opt(kind="cheap", affordable=True, effective_monthly=300),
        opt(kind="refinance", affordable=True, effective_monthly=400),   # matches lower_payment goal
    ]
    assert kinds(rank_options(opts, ["lower_payment"])) == ["refinance", "cheap", "no_car", "cheap_rejected"]


# ---------- personas (Appendix B) ----------

def test_p1_maya():
    r = recommend(P1)
    assert kinds(r["recommendations"]) == ["lease_buyout", "buy_miles_new_lease"]
    rejected = {o["kind"]: o["rejection_reason"] for o in r["considered"] if not o["affordable"]}
    assert set(rejected) == {"return_new_lease", "return_walk_away"}            # both need $1,670 upfront
    assert all("one month of bills" in reason for reason in rejected.values())


def test_p2_reyes_baseline():
    r = recommend(P2)
    assert kinds(r["recommendations"]) == ["keep", "trade_in_upgrade"]           # Highlander affordable today
    assert r["relief_needed"] is False


def test_p3_daniel():
    r = recommend(P3)
    assert kinds(r["recommendations"]) == ["trade_in_upgrade", "refinance", "keep"]   # goal: newer_vehicle


def test_negative_surplus_hands_off_to_human():
    p = copy.deepcopy(P2)                                   # same as "income drop 20%" (NM-17)
    p["finances"].update(monthly_income=4960, monthly_surplus=-340)
    r = recommend(p)
    assert r["relief_needed"] is True
    assert kinds(r["recommendations"])[0] == "talk_to_advisor"
    assert {"extend_term", "payment_deferral"} <= set(kinds(r["considered"]))


def test_contract_fields_and_ranks():
    r = recommend(P1)
    assert [o["rank"] for o in r["recommendations"]] == [1, 2]
    for o in r["considered"]:
        assert {"affordable", "rejection_reason", "rank", "previous_rank"} <= o.keys()
        assert (o["rank"] is None) == (not o["affordable"])
        assert o["affordable"] or o["rejection_reason"]
    assert r["life_event_applied"] is None and r["finances_after_event"] is None


def test_recommend_does_not_mutate_input():
    before = copy.deepcopy(P1)
    recommend(P1)
    assert P1 == before