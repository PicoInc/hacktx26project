"""Generates mock Nessie-shaped bank files for each persona. Owner: Rodrigo. Story: NM-7."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

OUTPUT_FOLDER = Path(__file__).resolve().parent.parent / "data" / "mock_bank"

WINDOW_START_DATE = date(2026, 7, 24)
WINDOW_LENGTH_DAYS = 91
MONTHS_IN_WINDOW = 3

# Paychecks arrive every 2 weeks → 6 paychecks in 3 months
PAYCHECK_COUNT = 6
DAYS_BETWEEN_PAYCHECKS = 14
FIRST_PAYCHECK_DAY = 7

# Each random purchase starts between these amounts (before scaling)
MIN_PURCHASE_AMOUNT = 5
MAX_PURCHASE_AMOUNT = 120

STORE_NAMES = ["H-E-B", "Target", "Starbucks", "Shell", "Amazon",
               "Chipotle", "Walmart", "CVS", "Spotify", "Torchy's Tacos"]

# Settings for each customer. Numbers come from Appendix B of the backlog.
PERSONAS = {
    "p1": {
        "first_name": "Maya", "last_name": "Lopez",
        "checking_balance": 640, "savings_balance": 2600,
        "monthly_income": 2100, "monthly_spending": 520, "purchase_count": 30,
        "bills": [("Rent", 750), ("Toyota Financial Services", 284.37),
                  ("Phone", 45), ("Utilities", 70)],
    },
    "p2": {
        "first_name": "Elena", "last_name": "Reyes",
        "checking_balance": 2100, "savings_balance": 9000,
        "monthly_income": 6200, "monthly_spending": 1700, "purchase_count": 40,
        "bills": [("Mortgage", 2300), ("Toyota Financial Services", 564.76),
                  ("Car insurance", 240), ("Utilities", 230), ("Phone", 140),
                  ("Internet", 75), ("Streaming", 50)],
    },
    "p3": {
        "first_name": "Daniel", "last_name": "Kim",
        "checking_balance": 3400, "savings_balance": 15000,
        "monthly_income": 6500, "monthly_spending": 1500, "purchase_count": 35,
        "bills": [("Rent", 1700), ("Toyota Financial Services", 406.46),
                  ("Car insurance", 180), ("Utilities", 160), ("Phone", 90),
                  ("Internet", 70), ("Gym", 45), ("Streaming", 30),
                  ("Student loan", 120)],
    },
}


def make_paychecks(monthly_income):
    """Creates 6 paychecks, one every 2 weeks, that add up to 3 months of income."""
    total_income_in_window = monthly_income * MONTHS_IN_WINDOW
    paycheck_amount = round(total_income_in_window / PAYCHECK_COUNT, 2)

    paychecks = []
    for paycheck_number in range(PAYCHECK_COUNT):
        days_after_start = FIRST_PAYCHECK_DAY + DAYS_BETWEEN_PAYCHECKS * paycheck_number
        paycheck_date = WINDOW_START_DATE + timedelta(days=days_after_start)
        paychecks.append({
            "amount": paycheck_amount,
            "transaction_date": str(paycheck_date),
            "description": "Payroll",
        })
    return paychecks


def make_purchases(random_generator, monthly_spending, purchase_count):
    """Creates random store purchases that add up to exactly 3 months of spending."""
    total_spending_in_window = monthly_spending * MONTHS_IN_WINDOW

    random_amounts = [random_generator.uniform(MIN_PURCHASE_AMOUNT, MAX_PURCHASE_AMOUNT)
                      for _ in range(purchase_count)]

    scale_factor = total_spending_in_window / sum(random_amounts)
    final_amounts = [round(amount * scale_factor, 2) for amount in random_amounts]

    final_amounts[-1] = round(total_spending_in_window - sum(final_amounts[:-1]), 2)

    day_offsets = sorted(random_generator.randint(0, WINDOW_LENGTH_DAYS - 1)
                         for _ in range(purchase_count))

    purchases = []
    for amount, day_offset in zip(final_amounts, day_offsets):
        purchase_date = WINDOW_START_DATE + timedelta(days=day_offset)
        purchases.append({
            "amount": amount,
            "purchase_date": str(purchase_date),
            "description": random_generator.choice(STORE_NAMES),
        })
    return purchases


def make_bills(bill_list):
    """Turns the (payee, amount) pairs into Nessie-shaped recurring bills."""
    return [{"payment_amount": amount, "payee": payee, "status": "recurring"}
            for payee, amount in bill_list]


def build_bank_data(customer_id, persona_settings):
    """Builds one customer's full bank data in Nessie's shape."""
    # Same seed every run → the "random" data is identical each time
    random_generator = random.Random(customer_id)

    return {
        "source": "synthetic",
        "customer": {
            "_id": customer_id,
            "first_name": persona_settings["first_name"],
            "last_name": persona_settings["last_name"],
        },
        "accounts": [
            {"_id": f"{customer_id}-checking", "type": "Checking",
             "balance": persona_settings["checking_balance"]},
            {"_id": f"{customer_id}-savings", "type": "Savings",
             "balance": persona_settings["savings_balance"]},
        ],
        "deposits": make_paychecks(persona_settings["monthly_income"]),
        "purchases": make_purchases(random_generator,
                                    persona_settings["monthly_spending"],
                                    persona_settings["purchase_count"]),
        "bills": make_bills(persona_settings["bills"]),
    }


def main():
    for customer_id, persona_settings in PERSONAS.items():
        bank_data = build_bank_data(customer_id, persona_settings)
        output_file = OUTPUT_FOLDER / f"{customer_id}.json"
        with open(output_file, "w") as file:
            json.dump(bank_data, file, indent=2)
        print(f"✓ wrote {customer_id}.json ({len(bank_data['purchases'])} purchases)")


if __name__ == "__main__":
    main()