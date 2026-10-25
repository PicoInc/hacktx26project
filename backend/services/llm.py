"""LLM explanations + number validator. Owner: Jose. Story: NM-13 / NM-14."""
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from services.templates import format_money, template_explanation

logger = logging.getLogger(__name__)

TIMEOUT_S = 6            # how long a customer waits before we show the template
HTTP_TIMEOUT_MS = 10000  # SDK ceiling; the Gemini API rejects deadlines under 10 s
DEFAULT_MODEL = "gemini-3.5-flash-lite"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "explain.txt"

_client = None
_warm_future = None
# Room for a warm-up plus timed-out requests still finishing in the background
_pool = ThreadPoolExecutor(max_workers=4)


def _system_prompt() -> str:
    lines = PROMPT_PATH.read_text(encoding="utf-8").splitlines()
    return "\n".join(line for line in lines if not line.startswith("#")).strip()


def _first_name(name: str) -> str:
    """'Maya Lopez' -> 'Maya'; a household like 'The Reyes family' stays whole."""
    if name.lower().startswith("the "):
        return "the " + name[4:]
    return name.split()[0] if name.split() else name


def _signed_money(n: float) -> str:
    if n > 0:
        return "+" + format_money(n)
    if n < 0:
        return "-" + format_money(-n)
    return format_money(0)


def _option_payload(rec: dict) -> dict:
    """Only the fields the model needs, with money already formatted so it can copy it verbatim."""
    payload = {
        "id": rec["id"],
        "title": rec["title"],
        "monthly_payment": format_money(rec["monthly_payment"]),
        "delta_monthly": _signed_money(rec["delta_monthly"]),
        "upfront_cost": format_money(rec["upfront_cost"]),
        "total_cost": format_money(rec["total_cost"]),
        "tradeoffs": rec.get("tradeoffs", []),
        "action_label": (rec.get("action") or {}).get("label", ""),
    }
    if rec.get("rejection_reason"):
        payload["rejection_reason"] = rec["rejection_reason"]
    return payload


def _build_user_content(recommendations: list[dict], profile: dict, life_event: dict | None) -> str:
    return json.dumps({
        "customer_first_name": _first_name(profile["customer"]["name"]),
        "life_event": life_event,
        "options": [_option_payload(r) for r in recommendations],
    })


def _model() -> str:
    return os.environ.get("LLM_MODEL", DEFAULT_MODEL)


def _get_client():
    """One shared client, so every request reuses the same open connection."""
    global _client
    from google import genai
    from google.genai import types

    if _client is None:
        _client = genai.Client(
            api_key=os.environ["LLM_API_KEY"],
            http_options=types.HttpOptions(timeout=HTTP_TIMEOUT_MS),
        )
    return _client


def _call_llm(system: str, user: str) -> str:
    """One Gemini call that returns JSON text. Raises on a missing key, timeout or API error."""
    from google.genai import types

    response = _get_client().models.generate_content(
        model=_model(),
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            temperature=0.3,
            # Minimal hidden reasoning: ~1 s instead of ~4 s on flash-lite
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    return response.text


def _warm_up():
    try:
        _get_client().models.get(model=_model())
        logger.info("LLM connection warmed up (%s)", _model())
    except Exception as exc:
        logger.warning("LLM warm-up failed (requests will still work or fall back): %r", exc)


def warm_up():
    """Called once when Flask starts: opens the TLS connection and checks the key/model in the
    background, so the first customer doesn't pay for it. Uses models.get, not generate_content,
    so it doesn't count against the per-minute generation quota. Runs at most once per process;
    returns its Future, or None without a key."""
    global _warm_future
    if _warm_future is None and os.environ.get("LLM_API_KEY"):
        _warm_future = _pool.submit(_warm_up)
    return _warm_future


def _call_with_deadline(system: str, user: str) -> str:
    """Wait at most TIMEOUT_S for the model; a straggling request finishes in the background and is ignored."""
    return _pool.submit(_call_llm, system, user).result(timeout=TIMEOUT_S)


def explain_all(recommendations: list[dict], profile: dict, life_event: dict | None) -> dict[str, dict]:
    """One LLM call for all options. Any problem falls back to the template, per option.
    Returns { option_id: { "text": str, "source": "llm" | "template" } }. Never raises."""
    out = {r["id"]: {"text": template_explanation(r), "source": "template"} for r in recommendations}
    if not recommendations or not os.environ.get("LLM_API_KEY"):
        return out

    try:
        raw = _call_with_deadline(_system_prompt(), _build_user_content(recommendations, profile, life_event))
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response is not a JSON object")
    except Exception as exc:  # timeout, network, bad key, bad JSON: the endpoint must still return 200
        logger.warning("LLM explanation failed, using templates: %r", exc)
        return out

    for rec in recommendations:
        text = parsed.get(rec["id"])
        if isinstance(text, str) and text.strip():
            # NM-14: validate(text, rec) here; keep the template when it fails
            out[rec["id"]] = {"text": text.strip(), "source": "llm"}
    return out
