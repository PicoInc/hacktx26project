"""Shared engine assumptions. All values are SYNTHETIC demo assumptions. Owner: Samu (NM-4)."""
import json
from pathlib import Path


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

   # Vehicle catalog: loaded from backend/data/vehicle_catalog.json (single source of truth)
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
with open(_DATA_DIR / "vehicle_catalog.json", encoding="utf-8") as _file:
    VEHICLE_CATALOG = json.load(_file)["vehicles"]