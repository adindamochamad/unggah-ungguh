from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from app.labeller import label_text
from app.labeller.arbitrate import arbitrate
from app.labeller.lexicon import PassResult, lexicon_label
from app.labeller.model import model_label
from app.main import app
from app.paths import corpus_path
from app.schema import SCHEMA_VERSION, LabelResponse, schema_document


client = TestClient(app)


def test_schema_endpoint():
    r = client.get("/schema")
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == SCHEMA_VERSION
    assert "Has register" in body["properties"]
    assert schema_document()["schema_version"] == SCHEMA_VERSION


def test_label_all_corpus_schema_valid():
    data = yaml.safe_load(corpus_path().read_text(encoding="utf-8"))
    for row in data["sentences"]:
        r = client.post("/label", json={"text": row["text"]})
        assert r.status_code == 200, row["id"]
        parsed = LabelResponse.model_validate(r.json())
        assert parsed.schema_version == SCHEMA_VERSION


def test_disagreement_yields_undetermined():
    # Lexicon sees krama-only pair words (pirsa, toya) plus ngoko address.
    # Model morph list does not include pirsa/toya, so it can vote ngoko.
    text = "Kowe pirsa toya kuwi"
    lex = lexicon_label(text)
    model = model_label(text)
    result = arbitrate(text, lex, model, "rules-v0")
    if lex.register != model.register:
        assert result.register == "undetermined"
        assert result.agreement is False
        assert result.evidence.lexicon_reading["register"] == lex.register
        assert result.evidence.model_reading["register"] == model.register
    else:
        # If this particular string happens to agree, still assert the rule
        # with synthetic passes.
        left = PassResult("krama", "undetermined", "deferential", hits=["panjenengan"])
        right = PassResult("ngoko", "undetermined", "peer", hits=[])
        forced = arbitrate("x", left, right, "rules-v0")
        assert forced.register == "undetermined"
        assert forced.agreement is False
        assert forced.evidence.lexicon_reading["register"] == "krama"
        assert forced.evidence.model_reading["register"] == "ngoko"


def test_forced_disagreement_undetermined():
    left = PassResult("krama", "banyumasan", "deferential", hits=["panjenengan"])
    right = PassResult("ngoko", "mataraman", "peer", hits=[])
    out = arbitrate("x", left, right, "rules-v0")
    assert out.register == "undetermined"
    assert out.dialect == "undetermined"
    assert out.stance == "undetermined"
    assert out.agreement is False


def test_agreement_keeps_value():
    left = PassResult("ngoko", "mataraman", "peer", hits=["kowe"])
    right = PassResult("ngoko", "mataraman", "peer", hits=[])
    out = arbitrate("x", left, right, "rules-v0")
    assert out.agreement is True
    assert out.register == "ngoko"
    assert out.dialect == "mataraman"
    assert out.stance == "peer"


def test_lexicon_runs_before_model():
    from app.labeller import pipeline as p

    src = Path(p.__file__).read_text(encoding="utf-8")
    run = src.split("def label_text", 1)[1]
    assert run.index("lexicon_label") < run.index("model_label")
    assert run.index("model_label") < run.index("arbitrate")


def test_label_text_returns_evidence():
    out = label_text("Panjenengan sampun dhahar dereng?")
    assert out.schema_version == SCHEMA_VERSION
    assert isinstance(out.evidence.lexicon, list)
    assert out.evidence.model
