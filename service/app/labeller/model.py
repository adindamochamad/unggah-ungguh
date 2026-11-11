"""Second-pass model.

This is a *separate opinion* from the lexicon, not a replacement for it.
The default backend (`rules-v0`) is an independent heuristic: character
n-grams, krama morphology, and dialect phonology — not the krama/ngoko
word list. It is named honestly in EVAL.md.

A hosted LLM is optional via MODEL_BACKEND=openai. The spike does not
require it; CI and `make eval` must run offline.
"""

from __future__ import annotations

import os
import re

from app.labeller.lexicon import PassResult, stance_from_register_and_address, tokenize
from app.schema import Dialect, Register

MODEL_ID = os.environ.get("MODEL_ID", "rules-v0")

# Morphology / function words the lexicon file does not treat as pairs.
_KRAMA_MORPH = re.compile(
    r"\b("
    r"nyuwun|pangapunten|kersa|rumiyin|menika|punika|dhateng|rawuh|"
    r"ngendika|pangandikan|aturi|kula|kedah|nglampahi|dinten|sampun|"
    r"dereng|mboten|inggih|sinten|pundi|ngriki|griya|ageng|sae"
    r")\b",
    re.I,
)
_NGOKO_MORPH = re.compile(
    r"\b("
    r"aku|kowe|kon|arep|wis|wes|durung|ora|gak|ya|iki|kuwi|sapa|"
    r"ngendi|endi|kene|ayo|ndang|gelem|ngomong|nulis"
    r")\b",
    re.I,
)
_MADYA_MORPH = re.compile(r"\b(sampeyan|nedha|punika|menika|kula)\b", re.I)

# East Javanese / ngapak phonology and particles, independent of the pair list.
_TIMURAN = re.compile(r"\b(kon|cak|cah|ae|gak|endi|suroboyo|surabaya|wes)\b", re.I)
_BANYUMAS = re.compile(r"\b(inyong|rika|kiyen|dhisit|kepriwe|umah|kuwe|ngrampungna)\b", re.I)
_MATARAMAN = re.compile(r"\b(dhisik|menyang|kowe|ngendi)\b", re.I)


def model_label(text: str) -> PassResult:
    krama_n = len(_KRAMA_MORPH.findall(text))
    ngoko_n = len(_NGOKO_MORPH.findall(text))
    madya_n = len(_MADYA_MORPH.findall(text))

    register: Register = _vote(krama=krama_n, ngoko=ngoko_n, madya=madya_n)
    dialect: Dialect = _dialect(text)
    tokens = tokenize(text)
    address = [t for t in tokens if t in {"panjenengan", "njenengan", "sampeyan", "kowe", "kon", "rika"}]
    stance = stance_from_register_and_address(register, address, tokens)
    return PassResult(
        register=register,
        dialect=dialect,
        stance=stance,
        hits=[f"krama:{krama_n}", f"ngoko:{ngoko_n}", f"madya:{madya_n}"],
        notes={"model_id": MODEL_ID, "counts": {"krama": krama_n, "ngoko": ngoko_n, "madya": madya_n}},
    )


def _vote(krama: int, ngoko: int, madya: int) -> Register:
    scores = {"krama": krama, "ngoko": ngoko, "madya": madya}
    present = {k: v for k, v in scores.items() if v > 0}
    if not present:
        return "undetermined"
    ranked = sorted(present.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(ranked) == 1:
        return ranked[0][0]  # type: ignore[return-value]
    if ranked[0][1] == ranked[1][1]:
        return "mixed"
    if ranked[1][1] > 0 and ranked[0][1] <= ranked[1][1] + 1:
        return "mixed"
    return ranked[0][0]  # type: ignore[return-value]


def _dialect(text: str) -> Dialect:
    scores = {
        "jawa-timuran": len(_TIMURAN.findall(text)),
        "banyumasan": len(_BANYUMAS.findall(text)),
        "mataraman": len(_MATARAMAN.findall(text)),
    }
    present = {k: v for k, v in scores.items() if v > 0}
    if not present:
        return "undetermined"
    ranked = sorted(present.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return "undetermined"
    return ranked[0][0]  # type: ignore[return-value]
