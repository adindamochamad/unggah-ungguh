"""Honest evaluation against the 30-sentence author corpus.

No accuracy threshold. An unflattering number that is correctly reported
is a pass.
"""

from __future__ import annotations

from datetime import date

import yaml

from app.labeller import label_text
from app.labeller.lexicon import LEXICON_VERSION, load_lexicon
from app.labeller.model import MODEL_ID
from app.paths import corpus_path, eval_out_path
from app.schema import DIMENSIONS, SCHEMA_VERSION


def load_corpus():
    with corpus_path().open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def confusion(pairs: list[tuple[str, str]]) -> dict[str, dict[str, int]]:
    labels = sorted({g for g, _ in pairs} | {p for _, p in pairs})
    table = {g: {p: 0 for p in labels} for g in labels}
    for g, p in pairs:
        table[g][p] += 1
    return table


def fmt_matrix(table: dict[str, dict[str, int]]) -> str:
    labels = list(table.keys())
    header = "gold \\ pred | " + " | ".join(labels)
    sep = "--- | " + " | ".join("---" for _ in labels)
    rows = [header, sep]
    for g in labels:
        cells = " | ".join(str(table[g].get(p, 0)) for p in labels)
        rows.append(f"{g} | {cells}")
    return "\n".join(rows)


# Honesty notes from the madya gold review. Not computed; they document
# corpus structure so a 0/9 madya row is not read as nine independent items.
_GOLD_REVIEW_NOTES = [
    "## Gold review (register)",
    "",
    "Operational definition used for `madya` gold: an utterance is madya when it is organized by characteristic mid-level lexicon (`sampeyan`, `nedha`, or a dialectal address standing in that same slot). `mixed` is reserved for more than one register with no such organizer. Krama or ngoko auxiliaries around that mid level do not by themselves make the gold `mixed`.",
    "",
    "Under that definition the nine madya gold labels were confirmed, not rewritten. Near-miss gold `krama` (`s28`, `s29`) was also confirmed: a dialect form (`umah`, `kiyen`) inside a `panjenengan` frame does not change the register gold.",
    "",
    "The madya gold row is **9 sentences / 4 patterns**, not nine independent items:",
    "",
    "1. `Sampeyan + [wis/sampun] + nedha + [durung/dereng]` — s13, s16, s19",
    "2. `Sampeyan kudu + verb + object + dina iki` — s15, s18, s21",
    "3. `Kula nyuwun tulung + address + maca naskah + demonstrative` — s14, s20",
    "4. `Kula nyuwun pangapunten + kersa ngomong` — s17",
    "",
    "s16 and s19 differ by `wes`/`wis` (the same word, two spellings). s15 and s21 differ by `menika`/`kiyen` and the verb. A reviewer who opens the corpus will see near-duplicates; **madya 0/9 is four patterns failing and then replicated across dialects.**",
    "",
    "Schema v0.1.0 conflates madya-as-lexicon with madya-as-mixture. Gold now uses the first sense; the labeller's mix rule implements the second. v0.2.0 must separate them. That is a finding, not a patch.",
    "",
    "Data notes, not corrected in this spike:",
    "",
    "- s17 contains Indonesian `pelan-pelan` (Javanese would be `alon-alon`). Tokens unknown to the lexicon are mostly Indonesian loans. Left in: realistic for civic Javanese writing.",
    "- s20 and s21 move register and dialect together (`rika`, `kiyen`). Dirty test design, and part of why arbitration returns `undetermined`. Left for v0.2.0.",
    "",
]


def accuracy(pairs: list[tuple[str, str]]) -> float:
    if not pairs:
        return 0.0
    return sum(1 for g, p in pairs if g == p) / len(pairs)


def main() -> None:
    corpus = load_corpus()
    sentences = corpus["sentences"]
    n = len(sentences)
    by_dim: dict[str, list[tuple[str, str]]] = {d: [] for d in DIMENSIONS}
    disagreements = 0

    for row in sentences:
        pred = label_text(row["text"])
        if not pred.agreement:
            disagreements += 1
        for dim in DIMENSIONS:
            by_dim[dim].append((row[dim], getattr(pred, dim)))

    lex = load_lexicon()
    lex_ver = lex.get("version", LEXICON_VERSION)
    lines = [
        "# EVAL — Unggah-Ungguh spike",
        "",
        f"- Date: {date.today().isoformat()}",
        f"- Schema version: {SCHEMA_VERSION}",
        f"- Lexicon version: {lex_ver}",
        f"- Model: `{MODEL_ID}` (independent heuristic second pass; not a neural LLM)",
        f"- Sample size: **{n}**. This is too small to generalise.",
        "- Corpus: author-written synthetic Javanese sentences, not BASAibu data.",
        "- Labeller order: lexicon → model → arbitrate (disagreement → undetermined).",
        "- Stance is derived only from register plus address forms.",
        f"- Lexicon/model disagreements on at least one dimension: {disagreements}/{n}",
        "",
        "No accuracy threshold is required to pass. These numbers are published as measured.",
        "",
    ]
    for dim in DIMENSIONS:
        pairs = by_dim[dim]
        acc = accuracy(pairs)
        table = confusion(pairs)
        lines.append(f"## {dim}")
        lines.append("")
        lines.append(f"Agreement with gold: {acc:.1%} ({sum(1 for g, p in pairs if g == p)}/{len(pairs)})")
        lines.append("")
        lines.append(fmt_matrix(table))
        lines.append("")

    lines.extend(_GOLD_REVIEW_NOTES)
    text = "\n".join(lines) + "\n"
    out = eval_out_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
