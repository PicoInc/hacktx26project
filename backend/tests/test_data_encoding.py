"""Data files are UTF-8 and must read the same on Windows (cp1252 default) as on macOS.
Without encoding="utf-8", the "·" in taglines shows up as "Â·" in the persona picker."""
from services.customer_profile import list_personas


def test_persona_taglines_decode_as_utf8():
    taglines = [p["tagline"] for p in list_personas()]
    assert any("·" in t for t in taglines)
    assert not any("Â" in t for t in taglines)
