"""Persona profiles for engine tests: same shape as GET /dashboard (Appendix B numbers)."""

P1 = {  # Maya: Corolla lease ending, over on miles
    "customer": {"id": "p1", "name": "Maya Lopez"},
    "goals": ["keep_a_car_after_graduation"],
    "miles_per_year": 11700,
    "vehicle_targets": ["corolla_le_2027"],
    "vehicle": {"catalog_id": "corolla_le_2023", "year": 2023, "model": "Corolla", "trim": "LE",
                "mileage": 31200, "est_value": 18900},
    "contract": {"type": "lease", "monthly_payment": 284.37, "months_elapsed": 32, "months_remaining": 4,
                 "residual": 14600, "payoff": 14600, "miles_allowed_total": 30000, "apr": 4.2},
    "finances": {"monthly_income": 2200, "monthly_bills": 1150, "monthly_spending": 520,
                 "monthly_surplus": 530, "savings": 2600, "checking": 640, "source": "mock"},
}

P2 = {  # Reyes family: RAV4 loan, baby on the way
    "customer": {"id": "p2", "name": "The Reyes family"},
    "goals": ["keep_payments_predictable"],
    "miles_per_year": 13000,
    "vehicle_targets": ["highlander_xle_2027"],
    "vehicle": {"catalog_id": "rav4_xle_2022", "year": 2022, "model": "RAV4", "trim": "XLE",
                "mileage": 41000, "est_value": 24000},
    "contract": {"type": "loan", "monthly_payment": 564.76, "apr": 4.9, "months_remaining": 38,
                 "payoff": 19841.0},
    "finances": {"monthly_income": 6200, "monthly_bills": 3600, "monthly_spending": 1700,
                 "monthly_surplus": 900, "savings": 9000, "checking": 2100, "source": "mock"},
}

P3 = {  # Daniel: high-APR Camry, positive equity
    "customer": {"id": "p3", "name": "Daniel Kim"},
    "goals": ["newer_vehicle", "lower_fuel_cost"],
    "miles_per_year": 12000,
    "vehicle_targets": ["camry_hybrid_se_2027"],
    "vehicle": {"catalog_id": "camry_se_2021", "year": 2021, "model": "Camry", "trim": "SE",
                "mileage": 48000, "est_value": 21000},
    "contract": {"type": "loan", "monthly_payment": 406.46, "apr": 9.9, "months_remaining": 36,
                 "payoff": 12615.0},
    "finances": {"monthly_income": 6500, "monthly_bills": 2800, "monthly_spending": 1500,
                 "monthly_surplus": 2200, "savings": 15000, "checking": 3400, "source": "mock"},
}