from app.wiki.client import parse_uulabels, render_uulabels, _strip_uulabels


def test_render_and_parse_roundtrip():
    wikitext = render_uulabels(
        {
            "register": "krama",
            "dialect": "banyumasan",
            "stance": "deferential",
            "state": "machine",
            "confidence": 0.72,
            "schema": "0.1.0",
            "labelled": "2026-11-11",
        }
    )
    parsed = parse_uulabels(wikitext)
    assert parsed is not None
    assert parsed["register"] == "krama"
    assert parsed["dialect"] == "banyumasan"
    assert parsed["confidence"] == "0.72"


def test_human_override_omits_confidence():
    wikitext = render_uulabels(
        {
            "register": "ngoko",
            "dialect": "mataraman",
            "stance": "peer",
            "state": "author-corrected",
            "confidence": None,
            "schema": "0.1.0",
            "labelled": "2026-11-11",
        }
    )
    assert "confidence" not in wikitext
    assert "author-corrected" in wikitext


def test_strip_keeps_body():
    page = "Panjenengan sampun dhahar dereng?\n\n" + render_uulabels(
        {"register": "krama", "dialect": "mataraman", "stance": "deferential", "state": "machine"}
    )
    body = _strip_uulabels(page)
    assert "Panjenengan" in body
    assert "UULabels" not in body
