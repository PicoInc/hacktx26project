"""Tests for LLM explanations and the template fallback. Owner: Jose. Story: NM-13."""
import json

import pytest

from engine.recommend import recommend
from engine.tests.fixtures import P1
from services import llm
from services.templates import format_money, template_explanation

ALLOWED_KEYS = {"id", "title", "monthly_payment", "delta_monthly", "upfront_cost", "total_cost",
                "tradeoffs", "action_label", "rejection_reason"}


@pytest.fixture
def recs():
    # First 3 of `considered` (not `recommendations`) so the tests always have 3 options,
    # including rejected ones that carry a rejection_reason
    return recommend(P1)["considered"][:3]


@pytest.fixture(autouse=True)
def api_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")


def fake_llm(monkeypatch, response):
    """Replace the network call; returns the list of (system, user) calls made."""
    calls = []

    def _fake(system, user):
        calls.append((system, user))
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(llm, "_call_llm", _fake)
    return calls


def test_llm_text_is_used(monkeypatch, recs):
    fake_llm(monkeypatch, json.dumps({r["id"]: f"Explanation for {r['id']}" for r in recs}))
    out = llm.explain_all(recs, P1, None)
    assert set(out) == {r["id"] for r in recs}
    assert all(v["source"] == "llm" for v in out.values())
    assert out[recs[0]["id"]]["text"] == f"Explanation for {recs[0]['id']}"


def test_one_call_for_all_options(monkeypatch, recs):
    calls = fake_llm(monkeypatch, "{}")
    llm.explain_all(recs, P1, None)
    assert len(calls) == 1


def test_timeout_falls_back_to_templates(monkeypatch, recs):
    fake_llm(monkeypatch, TimeoutError("timed out"))
    out = llm.explain_all(recs, P1, None)
    assert all(v["source"] == "template" and v["text"] for v in out.values())


def test_slow_model_hits_the_deadline(monkeypatch, recs):
    import time
    monkeypatch.setattr(llm, "TIMEOUT_S", 0.05)
    monkeypatch.setattr(llm, "_call_llm", lambda system, user: time.sleep(0.5) or "{}")
    start = time.time()
    out = llm.explain_all(recs, P1, None)
    assert time.time() - start < 0.4
    assert all(v["source"] == "template" for v in out.values())


def test_bad_json_falls_back_to_templates(monkeypatch, recs):
    fake_llm(monkeypatch, "not json at all")
    out = llm.explain_all(recs, P1, None)
    assert all(v["source"] == "template" for v in out.values())


def test_non_object_json_falls_back(monkeypatch, recs):
    fake_llm(monkeypatch, json.dumps(["a", "b"]))
    assert all(v["source"] == "template" for v in llm.explain_all(recs, P1, None).values())


def test_missing_or_invalid_ids_fall_back_individually(monkeypatch, recs):
    first, second, third = (r["id"] for r in recs)
    fake_llm(monkeypatch, json.dumps({first: "Good text", second: 42}))
    out = llm.explain_all(recs, P1, None)
    assert out[first]["source"] == "llm"
    assert out[second]["source"] == "template"
    assert out[third]["source"] == "template"


def test_no_api_key_skips_the_call(monkeypatch, recs):
    monkeypatch.delenv("LLM_API_KEY")
    calls = fake_llm(monkeypatch, "{}")
    out = llm.explain_all(recs, P1, None)
    assert calls == []
    assert all(v["source"] == "template" for v in out.values())


def test_payload_only_has_allowed_fields_and_formatted_money(monkeypatch, recs):
    calls = fake_llm(monkeypatch, "{}")
    llm.explain_all(recs, P1, {"type": "new_baby", "params": {}})
    sent = json.loads(calls[0][1])
    assert sent["customer_first_name"] == "Maya"
    assert sent["life_event"] == {"type": "new_baby", "params": {}}
    assert len(sent["options"]) == len(recs)
    for option in sent["options"]:
        assert set(option) <= ALLOWED_KEYS
    buyout = next(o for o in sent["options"] if o["id"] == "lease_buyout")
    assert buyout["monthly_payment"] == "$294.34"
    assert buyout["delta_monthly"].startswith("+$")
    assert buyout["upfront_cost"] == "$0"
    assert "rejection_reason" not in buyout
    rejected = next(o for o in sent["options"] if o["id"].startswith("buy_miles_new_lease"))
    assert rejected["rejection_reason"]


def test_system_prompt_strips_comment_header():
    prompt = llm._system_prompt()
    assert prompt and not any(line.startswith("#") for line in prompt.splitlines())
    assert "Do not calculate" in prompt


def test_first_name():
    assert llm._first_name("Maya Lopez") == "Maya"
    assert llm._first_name("The Reyes family") == "the Reyes family"


def test_format_money():
    assert format_money(1160) == "$1,160"
    assert format_money(294.34) == "$294.34"
    assert format_money(17660.4) == "$17,660.40"
    assert format_money(0) == "$0"


def test_template_explanation(recs):
    buyout = next(r for r in recs if r["id"] == "lease_buyout")
    text = template_explanation(buyout)
    assert text.startswith("Buy out your Corolla: $294.34/mo for 60 months.")
    assert text.endswith("Start buyout.")


def test_template_drops_zero_term():
    option = {"title": "Return the car", "monthly_payment": 0, "term_months": 0,
              "tradeoffs": ["No car payment"], "action": {"label": "Talk to a TFS specialist"}}
    text = template_explanation(option)
    assert "for 0 months" not in text
    assert text == "Return the car: $0/mo. No car payment. Talk to a TFS specialist."
