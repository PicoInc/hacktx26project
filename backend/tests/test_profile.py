"""Tests for the financial profile adapter. Owner: Rodrigo. Story: NM-7."""
import pytest

from services.profile import get_financial_profile

ALLOWED_DIFFERENCE = 5  # dollars; the backlog allows ±$5

# Expected monthly numbers for each customer, copied from Appendix B
EXPECTED_FINANCES = {
    "p1": {"monthly_income": 2100, "monthly_bills": 1150, "monthly_spending": 520,
           "monthly_surplus": 430, "savings": 2600, "checking": 640},
    "p2": {"monthly_income": 6200, "monthly_bills": 3600, "monthly_spending": 1700,
           "monthly_surplus": 900, "savings": 9000, "checking": 2100},
    "p3": {"monthly_income": 6500, "monthly_bills": 2800, "monthly_spending": 1500,
           "monthly_surplus": 2200, "savings": 15000, "checking": 3400},
}


@pytest.mark.parametrize("customer_id", ["p1", "p2", "p3"])
def test_finances_match_appendix_b(customer_id):
    finances = get_financial_profile(customer_id)
    expected = EXPECTED_FINANCES[customer_id]

    for field_name, expected_value in expected.items():
        assert finances[field_name] == pytest.approx(expected_value, abs=ALLOWED_DIFFERENCE), \
            f"{customer_id} {field_name}: got {finances[field_name]}, expected about {expected_value}"

    assert finances["source"] == "mock"


def test_nessie_mode_is_not_ready_yet(monkeypatch):
    monkeypatch.setenv("DATA_MODE", "nessie")
    with pytest.raises(NotImplementedError):
        get_financial_profile("p1")


def test_unknown_customer_gives_clear_error():
    with pytest.raises(FileNotFoundError):
        get_financial_profile("nobody")