"""Labeller pipeline: lexicon first, model second, then agreement check.

Do not invert this order.
"""

from __future__ import annotations

from app.labeller.arbitrate import arbitrate
from app.labeller.lexicon import lexicon_label
from app.labeller.model import MODEL_ID, model_label
from app.schema import LabelResponse


def label_text(text: str) -> LabelResponse:
    lex = lexicon_label(text)
    model = model_label(text)
    return arbitrate(text, lex, model, MODEL_ID)
