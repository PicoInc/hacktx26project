import pytest
from engine.options import build_options
from engine.tests.fixtures import P1, P2, P3

money = lambda x: pytest.approx(x, abs=0.01)
REQUIRED_KEYS = {"id", "kind", "target", "title", "vehicle_label", "keeps_vehicle", "monthly_payment",
                 "delta_monthly", "upfront_cost", "term_months", "total_cost", "fuel_monthly",
                 "effective_monthly", "equity_used", "tradeoffs", "assumptions", "action"}


def by_kind(options):
    return {o["kind"]: o for o in options}


def test_every_option_has_full_shape():
    for p in (P1, P2, P3):
        for o in build_options(p, include_relief=True):
            assert REQUIRED_KEYS <= o.keys(), o["id"]
            assert o["action"]["kind"] in {"self_service", "follow_up", "offer"}
            assert o["assumptions"]["source"] == "synthetic"
            assert 1 <= len(o["tradeoffs"]) <= 3


def test_ids_are_unique():
    for p in (P1, P2, P3):
        ids = [o["id"] for o in build_options(p, include_relief=True)]
        assert len(ids) == len(set(ids))


def test_p1_lease_options():
    o = by_kind(build_options(P1))
    assert set(o) == {"lease_buyout", "return_new_lease", "buy_miles_new_lease", "return_walk_away"}
    assert o["lease_buyout"]["monthly_payment"] == money(294.34)
    assert o["lease_buyout"]["delta_monthly"] == money(9.97)
    assert o["buy_miles_new_lease"]["upfront_cost"] == money(1160)
    assert o["buy_miles_new_lease"]["monthly_payment"] == money(310.40)    
    assert o["return_new_lease"]["upfront_cost"] == money(1670)
    assert o["return_walk_away"]["keeps_vehicle"] is False


def test_p2_loan_options():
    o = by_kind(build_options(P2))
    assert o["keep"]["monthly_payment"] == money(564.76)
    assert o["trade_in_upgrade"]["monthly_payment"] == pytest.approx(797.33, abs=0.5)
    assert "refinance" not in o                      # 4.9% already beats 6.4%
    assert "extend_term" not in o                    # relief only when asked


def test_p2_relief_options():
    o = by_kind(build_options(P2, include_relief=True))
    assert o["extend_term"]["monthly_payment"] == pytest.approx(439.52, abs=0.5)
    assert o["payment_deferral"]["monthly_payment"] == 0
    # deferral must not look "free" for ranking: first-year average, not $0
    assert o["payment_deferral"]["effective_monthly"] > o["extend_term"]["effective_monthly"]


def test_p3_loan_options():
    o = by_kind(build_options(P3))
    assert o["refinance"]["monthly_payment"] == pytest.approx(386.06, abs=0.5)
    assert o["trade_in_upgrade"]["monthly_payment"] == pytest.approx(465.09, abs=0.5)
    assert o["trade_in_upgrade"]["equity_used"] == pytest.approx(8385, abs=1)
    assert o["trade_in_upgrade"]["fuel_monthly"] < o["keep"]["fuel_monthly"]


def test_effective_monthly_formula():
    for o in build_options(P1) + build_options(P3):
        assert o["effective_monthly"] == money(o["monthly_payment"] + o["fuel_monthly"] + o["upfront_cost"] / 12)


def test_unknown_contract_type():
    with pytest.raises(ValueError):
        build_options({**P1, "contract": {**P1["contract"], "type": "rental"}})