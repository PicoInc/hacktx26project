import pytest
from engine.finance import (loan_payment, loan_balance, lease_payment, apr_to_money_factor,
                            projected_end_miles, mileage_overage_fee, equity, monthly_fuel_cost)

money = lambda x: pytest.approx(x, abs=0.01)

def test_loan_payment_reference():
    assert loan_payment(30000, 4.9, 60) == money(564.76)   # p2 RAV4
    assert loan_payment(22000, 9.9, 72) == money(406.46)   # p3 Camry
    assert loan_payment(14900, 6.9, 60) == money(294.34)   # p1 buyout

def test_loan_balance_reference():
    assert loan_balance(30000, 4.9, 60, 22) == pytest.approx(19841, abs=1)
    assert loan_balance(22000, 9.9, 72, 36) == pytest.approx(12615, abs=1)

def test_lease_payment_reference():
    assert lease_payment(22500, 14600, 0.00175, 36) == money(284.37)
    assert apr_to_money_factor(4.8) == pytest.approx(0.002)

def test_mileage():
    assert projected_end_miles(31200, 32, 4) == 35100
    assert mileage_overage_fee(35100, 30000, 0.25) == money(1275)
    assert mileage_overage_fee(28000, 30000, 0.25) == 0

def test_equity_and_fuel():
    assert equity(18900, 14600) == 4300
    assert equity(10000, 12000) == -2000
    assert monthly_fuel_cost(12000, 32, 3.0) == money(93.75)

def test_edge_cases():
    assert loan_payment(12000, 0, 12) == money(1000)
    assert loan_balance(30000, 4.9, 60, 60) == pytest.approx(0, abs=0.01)
    with pytest.raises(ValueError): loan_payment(1000, 5, 0)
    with pytest.raises(ValueError): projected_end_miles(1000, 0, 4)
    with pytest.raises(ValueError): monthly_fuel_cost(12000, 0, 3.0)