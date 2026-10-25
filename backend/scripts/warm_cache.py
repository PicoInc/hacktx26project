"""Fills backend/cache/ with LLM explanations for every demo path. Owner: Jose. Story: NM-21.

    cd backend
    python scripts/warm_cache.py            # only what's missing (resumable)
    python scripts/warm_cache.py --force    # redo everything
    python scripts/warm_cache.py --only p2  # one customer

Needs LLM_API_KEY in backend/.env. Takes about 7 minutes: the free tier allows 5 requests per
minute, so real calls are spaced PAUSE_S apart. Commit backend/cache/*.json afterwards, and
re-run after ANY change to the engine, persona data or prompts/explain.txt (old entries stop
matching, so they'd be misses, not stale answers).
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so `services` / `engine` import

from dotenv import load_dotenv

from engine.recommend import recommend
from services import cache, llm
from services.customer_profile import build_profile, list_personas

PAUSE_S = 13          # between real LLM calls: keeps under 5 per minute
RETRY_WAIT_S = 60     # after a fallback (rate limit, timeout, rejected number)
RETRIES = 2
# Must match what the UI can send (WhatIfPanel.jsx): events with no params, and the income-drop slider
INCOME_DROP_PCTS = range(10, 41, 5)


def events():
    yield None
    yield {"type": "new_baby", "params": {}}
    yield {"type": "longer_commute", "params": {}}
    for pct in INCOME_DROP_PCTS:
        yield {"type": "income_drop", "params": {"pct": pct}}


def label(customer_id, event):
    if event is None:
        return f"{customer_id} baseline"
    pct = event["params"].get("pct")
    return f"{customer_id} {event['type']}" + (f" {pct}%" if pct is not None else "")


def warm(customers=None, force=False, sleep=time.sleep, out=print) -> dict:
    """Returns { "written": [...], "cached": [...], "failed": [...] } of combination labels."""
    result = {"written": [], "cached": [], "failed": []}
    calls = 0
    for persona in list_personas():
        customer_id = persona["customer_id"]
        if customers and customer_id not in customers:
            continue
        profile = build_profile(customer_id)
        for event in events():
            name = label(customer_id, event)
            recs = recommend(profile, event)["recommendations"]  # same call the route makes
            key = llm.explanation_key(recs, profile, event)

            if not force and cache.get(key) is not None:
                result["cached"].append(name)
                out(f"  cached   {name}")
                continue

            for attempt in range(RETRIES + 1):
                if calls:
                    sleep(PAUSE_S if attempt == 0 else RETRY_WAIT_S)
                calls += 1
                explanations = llm.explain_all(recs, profile, event, use_cache=False)  # always ask the model
                if all(e["source"] == "llm" for e in explanations.values()):
                    cache.put(key, explanations)
                    result["written"].append(name)
                    out(f"  written  {name}")
                    break
                out(f"  retry    {name} (attempt {attempt + 1}: some text fell back to a template)")
            else:
                result["failed"].append(name)
                out(f"  FAILED   {name}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="regenerate entries that are already cached")
    parser.add_argument("--only", nargs="+", metavar="ID", help="only these customers, e.g. p2")
    args = parser.parse_args(argv)

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    if cache.cache_only():
        print("CACHE_ONLY is on, which blocks LLM calls. Unset it to warm the cache.")
        return 2
    if not os.environ.get("LLM_API_KEY"):
        print("No LLM_API_KEY: set it in backend/.env first.")
        return 2

    print(f"Warming the explanation cache with {llm._model()} ...")
    result = warm(args.only, args.force)
    print(f"\n{len(result['written'])} written, {len(result['cached'])} already cached, "
          f"{len(result['failed'])} failed")
    print(f"Hallucinations caught by the number validator: {llm.hallucinations_caught}")
    if result["failed"]:
        print("Failed (re-run to retry just these):", ", ".join(result["failed"]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
