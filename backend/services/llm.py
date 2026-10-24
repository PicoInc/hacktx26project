"""LLM explanations + number validator. Owner: Jose. Story: NM-13 / NM-14."""


def explain_all(recommendations: list[dict], profile: dict, life_event: dict | None) -> dict[str, dict]:
    """Stub until NM-13: template text so Rodrigo's route works from day one.
    Returns { option_id: { "text": str, "source": "llm" | "template" } }."""
    out = {}
    for r in recommendations:
        out[r["id"]] = {"text": f'{r.get("title", "")}: ${r.get("monthly_payment", 0):,.2f}/mo.', "source": "template"}
    return out
