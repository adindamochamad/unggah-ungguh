"""Where lexicon and model disagree, do not pick a winner."""

from __future__ import annotations

from app.labeller.lexicon import PassResult
from app.schema import DIMENSIONS, LabelEvidence, LabelResponse, SCHEMA_VERSION


def arbitrate(text: str, lex: PassResult, model: PassResult, model_id: str) -> LabelResponse:
    readings = {}
    agreement_all = True
    for dim in DIMENSIONS:
        left = getattr(lex, dim)
        right = getattr(model, dim)
        if left == right:
            readings[dim] = left
        else:
            readings[dim] = "undetermined"
            agreement_all = False

    n_hits = len(lex.hits)
    if agreement_all:
        confidence = min(0.95, 0.55 + 0.08 * n_hits)
    else:
        confidence = min(0.5, 0.2 + 0.04 * n_hits)

    evidence = LabelEvidence(
        lexicon=lex.hits,
        lexicon_reading={
            "register": lex.register,
            "dialect": lex.dialect,
            "stance": lex.stance,
        },
        model=model_id,
        model_reading={
            "register": model.register,
            "dialect": model.dialect,
            "stance": model.stance,
        },
    )
    return LabelResponse(
        register=readings["register"],
        dialect=readings["dialect"],
        stance=readings["stance"],
        confidence=round(confidence, 2),
        schema_version=SCHEMA_VERSION,
        evidence=evidence,
        agreement=agreement_all,
    )
