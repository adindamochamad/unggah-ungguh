"""Lexicon-first register labeller.

Javanese register is partly decidable from vocabulary. This pass is the
auditable baseline: a Javanese speaker can inspect and extend the YAML.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.paths import lexicon_path
from app.schema import Dialect, Register, Stance

_TOKEN = re.compile(r"[A-Za-zÀ-ÿ]+", re.UNICODE)

LEXICON_VERSION = "0.1.0"


@dataclass
class PassResult:
    register: Register
    dialect: Dialect
    stance: Stance
    hits: list[str] = field(default_factory=list)
    notes: dict[str, Any] = field(default_factory=dict)


def _norm(word: str) -> str:
    return word.lower()


def tokenize(text: str) -> list[str]:
    return [_norm(t) for t in _TOKEN.findall(text)]


@lru_cache(maxsize=1)
def load_lexicon(path: str | None = None) -> dict[str, Any]:
    p = Path(path) if path else lexicon_path()
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data


def _index_pairs(data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Map surface form -> {register, pair_id, kind}."""
    index: dict[str, dict[str, str]] = {}
    for pair in data.get("pairs", []):
        pid = pair.get("id", pair.get("ngoko", ""))
        kind = pair.get("kind", "vocab")
        for register_key in ("ngoko", "madya", "krama"):
            val = pair.get(register_key)
            if not val:
                continue
            for form in _split_forms(val):
                index[_norm(form)] = {
                    "register": register_key,
                    "id": pid,
                    "kind": kind,
                }
    return index


def _split_forms(val: str) -> list[str]:
    return [v.strip() for v in str(val).split("/") if v.strip()]


def _marker_index(data: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for dialect, words in (data.get("dialect_markers") or {}).items():
        for w in words:
            out[_norm(w)] = dialect
    return out


def lexicon_label(text: str, path: str | None = None) -> PassResult:
    data = load_lexicon(path)
    tokens = tokenize(text)
    pair_index = _index_pairs(data)
    markers = _marker_index(data)

    register_counts = {"ngoko": 0, "madya": 0, "krama": 0}
    hits: list[str] = []
    address: list[str] = []
    dialect_counts: dict[str, int] = {}

    for tok in tokens:
        info = pair_index.get(tok)
        if info:
            register_counts[info["register"]] += 1
            hits.append(tok)
            if info["kind"] == "address":
                address.append(tok)
        dialect = markers.get(tok)
        if dialect:
            dialect_counts[dialect] = dialect_counts.get(dialect, 0) + 1

    register = _pick_register(register_counts)
    dialect = _pick_dialect(dialect_counts)
    stance = stance_from_register_and_address(register, address, tokens)
    return PassResult(
        register=register,
        dialect=dialect,
        stance=stance,
        hits=hits,
        notes={
            "register_counts": register_counts,
            "dialect_counts": dialect_counts,
            "address": address,
            "lexicon_version": data.get("version", LEXICON_VERSION),
        },
    )


def _pick_register(counts: dict[str, int]) -> Register:
    present = {k: v for k, v in counts.items() if v > 0}
    if not present:
        return "undetermined"
    ranked = sorted(present.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(ranked) == 1:
        return ranked[0][0]  # type: ignore[return-value]
    top, second = ranked[0][1], ranked[1][1]
    if top == second:
        return "mixed"
    if second > 0 and top < second * 3:
        # both families present with a non-trivial minority
        return "mixed"
    return ranked[0][0]  # type: ignore[return-value]


def _pick_dialect(counts: dict[str, int]) -> Dialect:
    if not counts:
        return "undetermined"
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return "undetermined"
    winner = ranked[0][0]
    if winner in ("mataraman", "jawa-timuran", "banyumasan"):
        return winner  # type: ignore[return-value]
    return "undetermined"


def stance_from_register_and_address(
    register: Register,
    address: list[str],
    tokens: list[str],
) -> Stance:
    """Spike rule: stance is derived only from register plus address forms.

    Assertive is additionally triggered by a small closed set of obligation
    words (kudu/kedah) because they mark posture toward the addressee.
    """
    deferential_addr = {"panjenengan", "njenengan", "sampeyan"}
    peer_addr = {"kowe", "kon", "rika"}
    addr_set = set(address) or (set(tokens) & (deferential_addr | peer_addr))

    has_defer = bool(addr_set & deferential_addr) or register == "krama"
    has_peer = bool(addr_set & peer_addr) or register == "ngoko"
    has_assert = any(t in {"kudu", "kedah"} for t in tokens)

    if has_assert and (has_defer or has_peer):
        if has_defer and has_peer:
            return "mixed"
        return "assertive"
    if has_defer and has_peer:
        return "mixed"
    if has_defer:
        return "deferential"
    if has_peer:
        return "peer"
    if register == "madya":
        return "deferential"
    return "undetermined"
