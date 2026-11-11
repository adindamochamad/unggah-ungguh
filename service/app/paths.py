from __future__ import annotations

import os
from pathlib import Path


def _candidates(env_name: str, *relative: str) -> Path:
    override = os.environ.get(env_name)
    if override:
        return Path(override)
    here = Path(__file__).resolve()
    roots = [here.parents[1], here.parents[2], Path("/app")]
    for root in roots:
        candidate = root.joinpath(*relative)
        if candidate.exists():
            return candidate
    return Path("/app").joinpath(*relative)


def lexicon_path() -> Path:
    return _candidates("LEXICON_PATH", "data", "lexicon", "krama_ngoko.yaml")


def corpus_path() -> Path:
    return _candidates("CORPUS_PATH", "data", "corpus.yaml")


def eval_out_path() -> Path:
    override = os.environ.get("EVAL_OUT")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "EVAL.md"
