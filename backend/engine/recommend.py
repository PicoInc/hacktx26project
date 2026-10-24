"""The ONLY engine function the API calls. Owner: Samu. Story: NM-11."""


def recommend(profile: dict, life_event: dict | None = None) -> dict:
    """Returns { recommendations, considered, relief_needed, life_event_applied, finances_after_event }."""
    raise NotImplementedError
