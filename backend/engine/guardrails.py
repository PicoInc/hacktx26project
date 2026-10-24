"""Affordability rules and deterministic ranking. Owner: Samu. Story: NM-11."""


def check_affordability(option: dict, finances: dict, current_payment: float) -> tuple[bool, str | None]:
    raise NotImplementedError


def rank_options(options: list[dict], goals: list[str]) -> list[dict]:
    raise NotImplementedError
