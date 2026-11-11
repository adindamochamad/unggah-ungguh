from __future__ import annotations

import yaml

from app.paths import corpus_path
from app.schema import (
    DIALECT_VALUES,
    REGISTER_VALUES,
    SCHEMA_VERSION,
    STANCE_VALUES,
)


def test_corpus_schema_and_coverage():
    path = corpus_path()
    raw = path.read_text(encoding="utf-8")
    assert "NOT BASAibu" in raw or "not BASAibu" in raw
    data = yaml.safe_load(raw)
    assert data["schema_version"] == SCHEMA_VERSION
    sentences = data["sentences"]
    assert len(sentences) == 30

    ids = [s["id"] for s in sentences]
    assert len(ids) == len(set(ids))

    registers = {s["register"] for s in sentences}
    dialects = {s["dialect"] for s in sentences}
    stances = {s["stance"] for s in sentences}

    for value in ("ngoko", "madya", "krama"):
        assert value in registers
    for value in ("mataraman", "jawa-timuran", "banyumasan"):
        assert value in dialects
    for value in ("peer", "deferential", "assertive"):
        assert value in stances

    pairs = {(s["register"], s["dialect"]) for s in sentences if s["register"] != "mixed"}
    for register in ("ngoko", "madya", "krama"):
        for dialect in ("mataraman", "jawa-timuran", "banyumasan"):
            assert (register, dialect) in pairs, f"missing {register} × {dialect}"

    for s in sentences:
        assert s["register"] in REGISTER_VALUES
        assert s["dialect"] in DIALECT_VALUES
        assert s["stance"] in STANCE_VALUES
        assert s["text"].strip()
        assert "http" not in s["text"].lower()
