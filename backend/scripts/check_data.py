"""Checks the synthetic Toyota data files. Owner: Rodrigo. Story: NM-6."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REQUIRED_PROFILE_KEYS = ["customer_id", "name", "tagline", "goals", "miles_per_year",
                         "vehicle_targets", "vehicle", "contract"]


def load(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


def main():
    catalog = load("vehicle_catalog.json")["vehicles"]
    profiles = load("toyota_profiles.json")["profiles"]
    offers = load("offers.json")["offers"]

    for p in profiles:
        missing = [k for k in REQUIRED_PROFILE_KEYS if k not in p]
        assert not missing, f"{p.get('customer_id')} is missing {missing}"

        model_id = p["vehicle"]["model_id"]
        assert model_id in catalog, f"{p['customer_id']}: unknown model_id {model_id}"

        for target in p["vehicle_targets"]:
            assert target in catalog, f"{p['customer_id']}: unknown target {target}"

        print(f"✓ {p['customer_id']} · {p['name']} · {catalog[model_id]['label']}")

    print(f"✓ {len(catalog)} vehicles · {len(offers)} offers")
    print("All data checks passed.")


if __name__ == "__main__":
    main()