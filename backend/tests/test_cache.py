"""Tests for the explanation cache and the warm script. Owner: Jose. Story: NM-21."""
import copy
import json
import sys
import time
from pathlib import Path

import pytest

from engine.recommend import recommend
from services import cache, llm
from services.customer_profile import build_profile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import warm_cache  # noqa: E402

EVENT = {"type": "income_drop", "params": {"pct": 20}}


@pytest.fixture(autouse=True)
def api_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")


@pytest.fixture
def profile():
    return build_profile("p1")


@pytest.fixture
def recs(profile):
    return recommend(profile)["recommendations"]


def fake_llm(monkeypatch, texts_for=None):
    """Replace the network call; returns the list of calls made. Default text uses only engine numbers."""
    calls = []

    def _fake(system, user):
        calls.append(user)
        options = json.loads(user)["options"]
        return json.dumps({o["id"]: f"Your payment is {o['monthly_payment']}." for o in options})

    monkeypatch.setattr(llm, "_call_llm", texts_for or _fake)
    return calls


def warmed(recs, profile, event=None, text=None):
    key = llm.explanation_key(recs, profile, event)
    cache.put(key, {r["id"]: {"text": text or f"Cached for {r['id']}", "source": "llm"} for r in recs})
    return key


# keys

def test_key_has_the_spec_shape_and_is_stable(recs, profile):
    key = llm.explanation_key(recs, profile, None)
    assert key.startswith("p1:none:")
    assert key == llm.explanation_key(copy.deepcopy(recs), profile, None)
    assert llm.explanation_key(recs, profile, EVENT).startswith("p1:income_drop:")


def test_key_changes_when_anything_the_model_sees_changes(recs, profile, monkeypatch):
    base = llm.explanation_key(recs, profile, EVENT)
    assert base != llm.explanation_key(recs, profile, {"type": "income_drop", "params": {"pct": 25}})
    assert base != llm.explanation_key(recs, profile, {"type": "new_baby", "params": {}})

    changed = copy.deepcopy(recs)
    changed[0]["monthly_payment"] += 5
    assert base != llm.explanation_key(changed, profile, EVENT)

    monkeypatch.setattr(llm, "_system_prompt", lambda: "a different prompt")
    assert base != llm.explanation_key(recs, profile, EVENT)


# explain_all with the cache

def test_hit_is_served_without_calling_the_llm(monkeypatch, recs, profile):
    calls = fake_llm(monkeypatch)
    warmed(recs, profile, text="From the cache")
    out = llm.explain_all(recs, profile, None)
    assert calls == []
    assert all(v == {"text": "From the cache", "source": "llm"} for v in out.values())


def test_hit_still_works_with_no_api_key(monkeypatch, recs, profile):
    monkeypatch.delenv("LLM_API_KEY")
    warmed(recs, profile)
    assert all(v["source"] == "llm" for v in llm.explain_all(recs, profile, None).values())


def test_cache_only_miss_uses_templates_and_never_calls_the_llm(monkeypatch, recs, profile):
    monkeypatch.setenv("CACHE_ONLY", "true")
    calls = fake_llm(monkeypatch)
    out = llm.explain_all(recs, profile, None)
    assert calls == []
    assert all(v["source"] == "template" and v["text"] for v in out.values())


def test_cache_only_hit_is_served(monkeypatch, recs, profile):
    monkeypatch.setenv("CACHE_ONLY", "true")
    warmed(recs, profile)
    assert all(v["source"] == "llm" for v in llm.explain_all(recs, profile, None).values())


def test_miss_without_cache_only_calls_the_llm_but_does_not_write(monkeypatch, recs, profile):
    calls = fake_llm(monkeypatch)
    out = llm.explain_all(recs, profile, None)
    assert len(calls) == 1
    assert all(v["source"] == "llm" for v in out.values())
    assert cache.get(llm.explanation_key(recs, profile, None)) is None


def test_stale_cached_text_with_unknown_numbers_is_replaced(monkeypatch, recs, profile):
    monkeypatch.setenv("CACHE_ONLY", "true")
    warmed(recs, profile, text="Only $199/mo at 2.9% for you.")
    assert all(v["source"] == "template" for v in llm.explain_all(recs, profile, None).values())


def test_template_entries_in_the_cache_are_not_trusted(monkeypatch, recs, profile):
    monkeypatch.setenv("CACHE_ONLY", "true")
    key = llm.explanation_key(recs, profile, None)
    cache.put(key, {r["id"]: {"text": "Fallback text", "source": "template"} for r in recs})
    assert all(v["text"] != "Fallback text" for v in llm.explain_all(recs, profile, None).values())


def test_corrupt_cache_file_is_a_miss_not_a_crash(monkeypatch, recs, profile):
    monkeypatch.setenv("CACHE_ONLY", "true")
    cache.CACHE_DIR.mkdir(parents=True)
    (cache.CACHE_DIR / "p1.json").write_text("{ not json", encoding="utf-8")
    out = llm.explain_all(recs, profile, None)
    assert all(v["source"] == "template" and v["text"] for v in out.values())


# cache file

def test_put_get_round_trip_and_readable_file(recs, profile):
    key = warmed(recs, profile, text="Explicación con acentos: más barato")
    assert cache.get(key)[recs[0]["id"]]["text"] == "Explicación con acentos: más barato"
    raw = (cache.CACHE_DIR / "p1.json").read_text(encoding="utf-8")
    assert "más barato" in raw and raw.startswith("{\n")


def test_cache_only_flag(monkeypatch):
    for value, expected in [("true", True), ("TRUE", True), ("1", True), ("false", False), ("", False)]:
        monkeypatch.setenv("CACHE_ONLY", value)
        assert cache.cache_only() is expected
    monkeypatch.delenv("CACHE_ONLY")
    assert cache.cache_only() is False


# warm script

def test_warm_covers_every_demo_path_and_resumes(monkeypatch):
    calls = fake_llm(monkeypatch)
    sleeps = []
    result = warm_cache.warm(sleep=sleeps.append, out=lambda *_: None)

    expected = 3 * (3 + len(warm_cache.INCOME_DROP_PCTS))  # 3 personas x (baseline, baby, commute, 7 slider values)
    assert len(result["written"]) == expected == 30
    assert result["failed"] == [] and len(calls) == expected
    assert set(sleeps) == {warm_cache.PAUSE_S} and len(sleeps) == expected - 1  # paced, not before the first call

    again = warm_cache.warm(sleep=sleeps.append, out=lambda *_: None)
    assert len(again["cached"]) == expected and again["written"] == [] and len(calls) == expected  # no new calls

    forced = warm_cache.warm(force=True, sleep=sleeps.append, out=lambda *_: None)
    assert len(forced["written"]) == expected and len(calls) == 2 * expected


def test_warm_never_writes_template_fallbacks(monkeypatch):
    def always_fails(system, user):
        raise TimeoutError("rate limited")

    monkeypatch.setattr(llm, "_call_llm", always_fails)
    sleeps = []
    result = warm_cache.warm(customers=["p2"], sleep=sleeps.append, out=lambda *_: None)
    assert result["written"] == [] and len(result["failed"]) == 10
    assert not list(cache.CACHE_DIR.glob("*.json")) if cache.CACHE_DIR.exists() else True
    assert warm_cache.RETRY_WAIT_S in sleeps  # waited out the rate limit before retrying


def test_warm_keys_match_what_the_route_looks_up(monkeypatch):
    """The route builds recs from build_profile + recommend; warming must produce the same keys."""
    fake_llm(monkeypatch)
    warm_cache.warm(customers=["p3"], sleep=lambda _: None, out=lambda *_: None)
    profile = build_profile("p3")
    for event in warm_cache.events():
        recs = recommend(profile, event)["recommendations"]
        assert cache.get(llm.explanation_key(recs, profile, event)) is not None, event


# endpoint

def test_endpoint_with_cache_only_is_fast_and_llm_written(monkeypatch):
    monkeypatch.setattr(llm, "_warm_future", object())  # skip the real network warm-up
    from app import create_app

    fake_llm(monkeypatch)
    warm_cache.warm(customers=["p1"], sleep=lambda _: None, out=lambda *_: None)

    monkeypatch.setenv("CACHE_ONLY", "true")
    monkeypatch.delenv("LLM_API_KEY")
    monkeypatch.setattr(llm, "_call_llm", lambda *_: pytest.fail("no network in CACHE_ONLY mode"))
    client = create_app().test_client()

    for body in (None, {"type": "new_baby", "params": {}}, {"type": "income_drop", "params": {"pct": 25}}):
        start = time.perf_counter()
        response = client.post("/api/customers/p1/recommendations", json={"life_event": body})
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        cards = response.get_json()["recommendations"]
        assert cards and all(c["explanation_source"] == "llm" for c in cards), body
        assert elapsed_ms < 200, f"{elapsed_ms:.0f} ms for {body}"
