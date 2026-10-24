"""Shared engine assumptions. All values are SYNTHETIC demo assumptions. Owner: Samu (NM-4)."""

# Lease
OVERAGE_RATE_PER_MILE = 0.25
PREPAID_MILES_RATE = 0.15
DISPOSITION_FEE = 395
PURCHASE_OPTION_FEE = 300
NEW_LEASE_MONEY_FACTOR = 0.00200
NEW_LEASE_TERM = 36

# Financing
USED_AUTO_APR = 6.9      # buyout financing
NEW_AUTO_APR = 5.9       # trade-in / new vehicle
REFI_APR = 6.4
BUYOUT_TERM = 60
NEW_TERM = 60
EXTENSION_MONTHS = 12
DEFERRAL_MONTHS = 2

# Costs / depreciation
FUEL_PRICE = 3.00
DEPRECIATION_PER_YEAR = 0.12

# Guardrails (NM-11)
PAYMENT_TO_INCOME_MAX = 0.15
SURPLUS_SHARE_MAX = 0.50
MIN_BUFFER_MONTHS = 1
RELIEF_SURPLUS_MIN = 0

VEHICLE_CATALOG = {
    "corolla_le_2023":      {"label": "2023 Corolla LE",      "msrp": None,  "mpg": 35, "lease_residual_pct": None},
    "corolla_le_2027":      {"label": "2027 Corolla LE",      "msrp": 23500, "mpg": 35, "lease_residual_pct": 0.62},
    "rav4_xle_2022":        {"label": "2022 RAV4 XLE",        "msrp": None,  "mpg": 30, "lease_residual_pct": None},
    "highlander_xle_2027":  {"label": "2027 Highlander XLE",  "msrp": 45500, "mpg": 25, "lease_residual_pct": 0.58},
    "camry_se_2021":        {"label": "2021 Camry SE",        "msrp": None,  "mpg": 32, "lease_residual_pct": None},
    "camry_hybrid_se_2027": {"label": "2027 Camry Hybrid SE", "msrp": 32500, "mpg": 51, "lease_residual_pct": 0.60},
}