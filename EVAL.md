# EVAL — Unggah-Ungguh spike

- Date: 2026-11-11
- Schema version: 0.1.0
- Lexicon version: 0.1.0
- Model: `rules-v0` (independent heuristic second pass; not a neural LLM)
- Sample size: **30**. This is too small to generalise.
- Corpus: author-written synthetic Javanese sentences, not BASAibu data.
- Labeller order: lexicon → model → arbitrate (disagreement → undetermined).
- Stance is derived only from register plus address forms.
- Lexicon/model disagreements on at least one dimension: 5/30

No accuracy threshold is required to pass. These numbers are published as measured.

## register

Agreement with gold: 66.7% (20/30)

gold \ pred | krama | madya | mixed | ngoko | undetermined
--- | --- | --- | --- | --- | ---
krama | 8 | 0 | 0 | 0 | 0
madya | 1 | 0 | 4 | 0 | 4
mixed | 0 | 0 | 0 | 0 | 1
ngoko | 0 | 0 | 0 | 12 | 0
undetermined | 0 | 0 | 0 | 0 | 0

## dialect

Agreement with gold: 70.0% (21/30)

gold \ pred | banyumasan | jawa-timuran | mataraman | undetermined
--- | --- | --- | --- | ---
banyumasan | 8 | 0 | 0 | 1
jawa-timuran | 0 | 8 | 0 | 1
mataraman | 0 | 0 | 5 | 7
undetermined | 0 | 0 | 0 | 0

## stance

Agreement with gold: 86.7% (26/30)

gold \ pred | assertive | deferential | mixed | peer | undetermined
--- | --- | --- | --- | --- | ---
assertive | 4 | 0 | 0 | 0 | 3
deferential | 0 | 12 | 0 | 1 | 0
mixed | 0 | 0 | 1 | 0 | 0
peer | 0 | 0 | 0 | 9 | 0
undetermined | 0 | 0 | 0 | 0 | 0

## Gold review (register)

Operational definition used for `madya` gold: an utterance is madya when it is organized by characteristic mid-level lexicon (`sampeyan`, `nedha`, or a dialectal address standing in that same slot). `mixed` is reserved for more than one register with no such organizer. Krama or ngoko auxiliaries around that mid level do not by themselves make the gold `mixed`.

Under that definition the nine madya gold labels were confirmed, not rewritten. Near-miss gold `krama` (`s28`, `s29`) was also confirmed: a dialect form (`umah`, `kiyen`) inside a `panjenengan` frame does not change the register gold.

The madya gold row is **9 sentences / 4 patterns**, not nine independent items:

1. `Sampeyan + [wis/sampun] + nedha + [durung/dereng]` — s13, s16, s19
2. `Sampeyan kudu + verb + object + dina iki` — s15, s18, s21
3. `Kula nyuwun tulung + address + maca naskah + demonstrative` — s14, s20
4. `Kula nyuwun pangapunten + kersa ngomong` — s17

s16 and s19 differ by `wes`/`wis` (the same word, two spellings). s15 and s21 differ by `menika`/`kiyen` and the verb. A reviewer who opens the corpus will see near-duplicates; **madya 0/9 is four patterns failing and then replicated across dialects.**

Schema v0.1.0 conflates madya-as-lexicon with madya-as-mixture. Gold now uses the first sense; the labeller's mix rule implements the second. v0.2.0 must separate them. That is a finding, not a patch.

Data notes, not corrected in this spike:

- s17 contains Indonesian `pelan-pelan` (Javanese would be `alon-alon`). Tokens unknown to the lexicon are mostly Indonesian loans. Left in: realistic for civic Javanese writing.
- s20 and s21 move register and dialect together (`rika`, `kiyen`). Dirty test design, and part of why arbitration returns `undetermined`. Left for v0.2.0.

