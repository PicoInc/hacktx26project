"""Tests for the number validator: the LLM may never show a number we didn't compute.
Owner: Jose. Story: NM-14."""
import json
import logging

import pytest

from engine.recommend import recommend
from engine.tests.fixtures import P1
from services import llm
from services.llm import allowed_numbers, extract_numbers, validate
from services.templates import format_money, template_explanation

BAD_STRING = "Good news: you can drive for only $199/mo at 2.9%."


@pytest.fixture
def buyout():
    return next(o for o in recommend(P1)["considered"] if o["id"] == "lease_buyout")


@pytest.fixture
def recs():
    return recommend(P1)["recommendations"]


@pytest.fixture(autouse=True)
def api_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")


def fake_llm(monkeypatch, texts_by_id):
    monkeypatch.setattr(llm, "_call_llm", lambda system, user: json.dumps(texts_by_id))


# extract_numbers

@pytest.mark.parametrize("text, expected", [
    ("a fee of $1,275", {1275.0}),
    ("1,275.00 total", {1275.0}),
    ("at 6.9% APR", {6.9}),
    ("a 60-month loan", {60.0}),
    ("$294.34/mo and $1,160 upfront", {294.34, 1160.0}),
    ("the fee is $1,275. Then", {1275.0}),        # sentence-ending period isn't a decimal
    ("pay $1,160, then relax", {1160.0}),         # trailing comma isn't a thousands separator
    ("a 2027 Corolla", {2027.0}),
    ("no numbers here", set()),
])
def test_extract_numbers(text, expected):
    assert extract_numbers(text) == expected


# allowed_numbers

def test_allowed_numbers_cover_fields_strings_and_rounding(buyout):
    allowed = allowed_numbers(buyout)
    assert round(buyout["monthly_payment"], 2) in allowed
    assert float(round(buyout["monthly_payment"])) in allowed        # "$294" for $294.34
    assert float(buyout["term_months"]) in allowed
    assert abs(round(buyout["delta_monthly"], 2)) in allowed          # sign is said in words
    assert buyout["assumptions"]["apr"] in allowed
    assert 1275.0 in allowed                                          # from the trade-off text
    assert 2023.0 in allowed                                          # from "2023 Corolla LE"


# validate

def test_bad_string_is_rejected(buyout):
    assert not validate(BAD_STRING, buyout)


def test_good_text_passes(buyout):
    text = (
        f"Maya, you can buy out your Corolla for {format_money(buyout['monthly_payment'])}/mo "
        f"over {buyout['term_months']} months, with {format_money(buyout['upfront_cost'])} upfront. "
        "It avoids the $1,275 over-mileage fee. You can start the buyout online."
    )
    assert validate(text, buyout)


def test_rounded_dollars_pass(buyout):
    whole = round(buyout["monthly_payment"])
    delta = round(abs(buyout["delta_monthly"]))
    assert validate(f"About ${whole}/mo, ${delta} more than today.", buyout)


def test_small_integers_used_as_words_are_ignored(buyout):
    assert validate("You have 2 options, and a specialist replies within 1 business day.", buyout)


def test_one_made_up_number_is_enough_to_reject(buyout):
    good = f"Your payment is {format_money(buyout['monthly_payment'])}/mo"
    assert not validate(good + " for 48 months.", buyout)


def test_life_event_numbers_are_allowed_only_when_passed(buyout):
    text = "With the extra $500 a month for the baby, this keeps things steady."
    assert not validate(text, buyout)
    assert validate(text, buyout, extra={500.0})


def test_template_always_passes_its_own_validation(recs):
    for rec in recs:
        assert validate(template_explanation(rec), rec)


# explain_all wiring

def test_hallucinated_text_falls_back_and_good_text_is_kept(monkeypatch, recs, caplog):
    assert len(recs) >= 2
    first, second = recs[0], recs[1]
    good = f"You can keep things simple at {format_money(first['monthly_payment'])}/mo."
    fake_llm(monkeypatch, {first["id"]: good, second["id"]: BAD_STRING})
    before = llm.hallucinations_caught

    with caplog.at_level(logging.WARNING, logger="services.llm"):
        out = llm.explain_all(recs, P1, None)

    assert out[first["id"]] == {"text": good, "source": "llm"}
    assert out[second["id"]] == {"text": template_explanation(second), "source": "template"}
    assert llm.hallucinations_caught == before + 1
    assert any("Validator rejected" in r.message and second["id"] in r.message for r in caplog.records)


def test_life_event_params_are_allowed_in_explain_all(monkeypatch, recs):
    rec = recs[0]
    text = f"Even with $500 more a month for the baby, {format_money(rec['monthly_payment'])}/mo fits."
    fake_llm(monkeypatch, {rec["id"]: text})
    event = {"type": "new_baby", "params": {"monthly_cost": 500}}
    assert llm.explain_all([rec], P1, event)[rec["id"]]["source"] == "llm"


# endpoint: never an empty explanation

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(llm, "_warm_future", object())   # skip the real network warm-up
    from app import create_app
    return create_app().test_client()


def test_endpoint_replaces_hallucinations_with_non_empty_templates(monkeypatch, client):
    monkeypatch.setattr(llm, "_call_llm", lambda system, user: json.dumps(
        {o["id"]: BAD_STRING for o in json.loads(user)["options"]}))
    response = client.post("/api/customers/p1/recommendations", json={"life_event": None})
    assert response.status_code == 200
    cards = response.get_json()["recommendations"]
    assert cards
    for card in cards:
        assert card["explanation"].strip()
        assert card["explanation_source"] == "template"
        assert "$199" not in card["explanation"]


def test_endpoint_survives_llm_errors(monkeypatch, client):
    def boom(system, user):
        raise RuntimeError("model down")
    monkeypatch.setattr(llm, "_call_llm", boom)
    response = client.post("/api/customers/p1/recommendations", json={"life_event": None})
    assert response.status_code == 200
    assert all(card["explanation"].strip() for card in response.get_json()["recommendations"])
