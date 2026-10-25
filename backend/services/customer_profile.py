"""Builds the full customer profile (engine input + dashboard base). Owner: Rodrigo. Story: NM-8."""
import json
from pathlib import Path

from engine.finance import loan_balance, projected_end_miles
from services.profile import get_financial_profile

# Folder with our data files: backend/data/
DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"

# A lease "money factor" × 2400 = its APR (e.g. 0.00175 × 2400 = 4.2%)
MONEY_FACTOR_TO_APR = 2400


class CustomerNotFound(Exception):
    """Raised when a customer id doesn't exist in toyota_profiles.json."""


def load_json(filename):
    """Opens a file from the data folder and returns its contents."""
    with open(DATA_FOLDER / filename) as file:
        return json.load(file)


def find_toyota_profile(customer_id):
    """Finds one customer in toyota_profiles.json, or raises CustomerNotFound."""
    for toyota_profile in load_json("toyota_profiles.json")["profiles"]:
        if toyota_profile["customer_id"] == customer_id:
            return toyota_profile
    raise CustomerNotFound(customer_id)


def list_personas():
    """Returns the short list of customers for the persona picker."""
    return [
        {"customer_id": toyota_profile["customer_id"],
         "name": toyota_profile["name"],
         "tagline": toyota_profile["tagline"]}
        for toyota_profile in load_json("toyota_profiles.json")["profiles"]
    ]

def build_vehicle(raw_vehicle, catalog):
    """Combines the customer's car data with the car facts from the catalog."""
    car_facts = catalog[raw_vehicle["model_id"]]
    return {
        "catalog_id": raw_vehicle["model_id"],
        "year": car_facts["year"],
        "model": car_facts["model"],
        "trim": car_facts["trim"],
        "mileage": raw_vehicle["mileage"],
        "est_value": raw_vehicle["est_value"],
    }


def build_lease_contract(raw_contract, current_mileage):
    """Builds a lease contract and calculates its APR, payoff and projected miles."""
    return {
        "type": "lease",
        "monthly_payment": raw_contract["monthly_payment"],
        "months_elapsed": raw_contract["months_elapsed"],
        "months_remaining": raw_contract["months_remaining"],
        "apr": round(raw_contract["money_factor"] * MONEY_FACTOR_TO_APR, 2),
        "residual": raw_contract["residual"],
        "payoff": raw_contract["residual"],
        "miles_allowed_total": raw_contract["miles_allowed_total"],
        "miles_projected_at_end": projected_end_miles(
            current_mileage,
            raw_contract["months_elapsed"],
            raw_contract["months_remaining"],
        ),
    }


def build_loan_contract(raw_contract):
    """Builds a loan contract and calculates how much is still owed (payoff)."""
    payoff = loan_balance(
        raw_contract["principal"],
        raw_contract["apr"],
        raw_contract["term_months"],
        raw_contract["payments_made"],
    )
    return {
        "type": "loan",
        "monthly_payment": raw_contract["monthly_payment"],
        "apr": raw_contract["apr"],
        "months_remaining": raw_contract["months_remaining"],
        "payoff": round(payoff, 2),
    }


def build_contract(raw_contract, current_mileage):
    """Picks the right builder depending on the contract type."""
    if raw_contract["type"] == "lease":
        return build_lease_contract(raw_contract, current_mileage)
    return build_loan_contract(raw_contract)



def build_profile(customer_id):
    """Returns the full profile for one customer. The engine and the dashboard both use it."""
    toyota_profile = find_toyota_profile(customer_id)
    catalog = load_json("vehicle_catalog.json")["vehicles"]

    return {
        "customer": {"id": customer_id, "name": toyota_profile["name"]},
        "goals": toyota_profile["goals"],
        "miles_per_year": toyota_profile["miles_per_year"],
        "vehicle_targets": toyota_profile["vehicle_targets"],
        "vehicle": build_vehicle(toyota_profile["vehicle"], catalog),
        "contract": build_contract(toyota_profile["contract"], toyota_profile["vehicle"]["mileage"]),
        "finances": get_financial_profile(customer_id),
    }