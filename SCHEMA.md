# Schema v0.1.0

Provisional by design. The fellowship's first quarter replaces this through
co-design with Javanese writers. Every value is contestable.

**Stance in this spike is derived only from register plus address forms.**
That is the most contestable of the three dimensions.

---

## Properties

### Has register — *Text*

| Value | English | Indonesian |
|---|---|---|
| `ngoko` | Informal Javanese register | Ragaman ngoko (akrab / tidak resmi) |
| `madya` | Mid register, between ngoko and krama | Ragaman madya (tengah) |
| `krama` | High / polite register | Ragaman krama (halus / hormat) |
| `mixed` | More than one register in the same text | Campuran ragam |
| `undetermined` | Labeller passes disagreed, or evidence was insufficient | Tidak ditentukan |

### Has dialect — *Text*

| Value | English | Indonesian |
|---|---|---|
| `mataraman` | Central Javanese (Yogyakarta / Surakarta sphere) | Dialek Mataraman |
| `jawa-timuran` | East Javanese (e.g. Surabaya and surrounds) | Dialek Jawa Timuran |
| `banyumasan` | Western Javanese / Ngapak | Dialek Banyumasan (Ngapak) |
| `undetermined` | Labeller passes disagreed, or evidence was insufficient | Tidak ditentukan |

### Has stance — *Text*

Derived here from register plus address forms (`kowe` / `kon` / `rika` vs `sampeyan` / `panjenengan`), plus a closed set of obligation words (`kudu` / `kedah`). Not a psychological profile of the author.

| Value | English | Indonesian |
|---|---|---|
| `peer` | Address among equals | Sikap setara |
| `deferential` | Address that marks respect toward the addressee | Sikap hormat |
| `assertive` | Obligation / directive toward the addressee | Sikap tegas / memerintah |
| `mixed` | More than one stance cue | Campuran sikap |
| `undetermined` | Labeller passes disagreed, or evidence was insufficient | Tidak ditentukan |

### Has label state — *Text*

| Value | English | Indonesian |
|---|---|---|
| `machine` | Written by the sidecar, not yet reviewed | Label mesin, belum ditinjau |
| `author-confirmed` | A human accepted the machine value | Penulis mengonfirmasi |
| `author-corrected` | A human replaced the value | Penulis memperbaiki |
| `author-rejected` | A human rejected the value without substituting another | Penulis menolak |

### Has label confidence — *Number*

0.0–1.0, **machine labels only**. Cleared on human override.

| English | Indonesian |
|---|---|
| How strongly the two passes agreed and how much lexicon evidence was present. Not a probability of truth. | Seberapa kuat kedua pass bersepakat dan seberapa banyak bukti leksikon. Bukan probabilitas kebenaran. |

### Has schema version — *Text*

Always `0.1.0` in this spike.

| English | Indonesian |
|---|---|
| Which schema produced the labels. | Versi skema yang dipakai untuk label. |

### Has labelled at — *Date*

ISO 8601 date.

| English | Indonesian |
|---|---|
| When the current labels were written. | Kapan label saat ini ditulis. |

---

## Wiki representation

```
{{UULabels
|register=krama
|dialect=banyumasan
|stance=deferential
|state=machine
|confidence=0.72
|schema=0.1.0
|labelled=2026-11-11
}}
```

Queryable:

```
{{#ask: [[Has register::krama]] |?Has dialect |?Has label state }}
```
