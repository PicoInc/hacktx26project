"""Data adapter: DATA_MODE=mock|nessie → normalized finances. Owner: Rodrigo. Story: NM-7."""
import json
import os
from pathlib import Path

# Folder with the mock bank files: backend/data/mock_bank/
MOCK_BANK_FOLDER = Path(__file__).resolve().parent.parent / "data" / "mock_bank"

# The bank data covers 3 months, so we divide totals by 3 to get monthly numbers
MONTHS_IN_WINDOW = 3


def load_mock_bank_data(customer_id):
    """Reads data/mock_bank/<customer_id>.json and returns its contents."""
    file_path = MOCK_BANK_FOLDER / f"{customer_id}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"No mock bank data for customer '{customer_id}'")
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def get_account_balance(accounts, account_type):
    """Adds up the balance of every account of one type ("Checking" or "Savings")."""
    return sum(account["balance"] for account in accounts if account["type"] == account_type)


def calculate_monthly_finances(bank_data, source):
    """Turns raw Nessie-shaped bank data into the monthly numbers the engine uses."""
    total_deposits = sum(deposit["amount"] for deposit in bank_data["deposits"])
    total_purchases = sum(purchase["amount"] for purchase in bank_data["purchases"])

    monthly_income = total_deposits / MONTHS_IN_WINDOW
    monthly_spending = total_purchases / MONTHS_IN_WINDOW
    monthly_bills = sum(bill["payment_amount"] for bill in bank_data["bills"]
                        if bill["status"] == "recurring")
    monthly_surplus = monthly_income - monthly_bills - monthly_spending

    return {
        "monthly_income": round(monthly_income, 2),
        "monthly_bills": round(monthly_bills, 2),
        "monthly_spending": round(monthly_spending, 2),
        "monthly_surplus": round(monthly_surplus, 2),
        "savings": get_account_balance(bank_data["accounts"], "Savings"),
        "checking": get_account_balance(bank_data["accounts"], "Checking"),
        "source": source,
    }


def get_financial_profile(customer_id: str) -> dict:
    """The only function other files call. Picks the data source from DATA_MODE."""
    data_mode = os.getenv("DATA_MODE", "mock")

    if data_mode == "mock":
        bank_data = load_mock_bank_data(customer_id)
        return calculate_monthly_finances(bank_data, source="mock")

    if data_mode == "nessie":
        raise NotImplementedError("DATA_MODE=nessie is not implemented yet (NM-25). Use DATA_MODE=mock.")

    raise ValueError(f"Unknown DATA_MODE '{data_mode}'. Use 'mock' or 'nessie'.")