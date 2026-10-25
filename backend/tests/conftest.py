"""Shared test setup. Owner: Jose."""
import pytest

from services import cache


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Tests never read the committed backend/cache/ files (a hit would skip the fake LLM) and
    never run in CACHE_ONLY mode unless they ask for it."""
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.delenv("CACHE_ONLY", raising=False)
