# Newsletter taxonomy — three sections, seven tags

Settled 2026-10-01, measured on all **904 published articles across 74 AiPulse issues**.

Written for the weekly. The daily keeps collecting and analysing unchanged; this governs how a
published story is filed.

---

## Why the current pillars had to go

An item's pillar is the DEVONthink group it was **collected** from:

```python
PILLARS = {"AiPulse: Humor": "grin_and_think", "AiPulse: Global": "global_lens", ...}
```

So a pillar records provenance, never subject. Measured consequences across the archive:

| pillar | items | what it actually held |
|---|---|---|
| `humor` | 85 | **80 from interestingengineering + newatlas** — nuclear fuel reprocessing, a hybrid airliner, a superintelligence ban. A content classifier agreed with the label on **2%** of them. |
| `global` | 298 | 33% of everything, defined by SOURCE COUNTRY, not subject |
| `explainer` | 65 | 54 from one blogger (simonwillison.net), several of them release notes |
| `career` | 3 | in 74 issues |

The deeper fault: **the old scheme mixed three axes.** `pulse`/`profession`/`explainer`/`frontier`
are about content, `global` is about origin, `multimedia` is about format. A story can be all
three at once, so forcing one answer guarantees wrong ones — and origin and format are already
known for free from the feed and the URL, so no model should be asked to guess them.

---

## The three sections

Each answers a question the reader is actually asking. Shares are the measured split of the
904-article archive.

| section | the question | holds | share | ~per week |
|---|---|---|---|---|
| **Ne oldu?** | what happened | `models`, `donanim` | 33% | 28 |
| **Ne işe yarıyor?** | what is it for | `uygulama`, `bilim` | 32% | 28 |
| **Ne düşünmeli?** | what to make of it | `kuram`, `politika`, `olaylar` | 35% | 30 |

Balance was the deciding factor, not accuracy. Four groupings were tested and **all scored
85–87%** against hand labels — on 60 articles that is a one-article spread, i.e. noise. The
alternatives put 45–52% of the newsletter in a single section, which is the `global`-at-33%
problem relabelled. This one is the only even split.

**Choose the section count for the reader. The model is indifferent.**

---

## The seven tags

The section is derived; the tag is what the model assigns and what a reader filters on.

| tag | definition |
|---|---|
| `models` | A named model or system, or the organisation building it: releases, capabilities, benchmarks of a named model, funding, acquisitions, lab strategy. |
| `kuram` | How AI works. Methods, architectures, training, interpretability, limits, evaluation as a science. |
| `bilim` | What we learned about the WORLD, **with AI as the instrument**. The discovery belongs to another field and AI was the tool that reached it. |
| `uygulama` | What changed in a field of work — medicine, construction, farming, law, education, media, manufacturing. The news is that a SECTOR changed. |
| `donanim` | What AI runs on: chips, accelerators, data centres, memory and interconnect, fabs, supply chain, power and cooling for compute. |
| `politika` | Who sets the rules: regulation, law, courts, export controls, national strategy, standards, state security, geopolitics. |
| `olaylar` | What went wrong: failures, outages, misuse, bias, deepfakes, scams, breaches, harms, lawsuits over them, safety tests a model failed. |

### Boundary tests

These exist because a 7-way choice is undecidable without them. Each is a question with an
answer, not a vibe:

- A model that does something in a field → **uygulama** if the news is that the FIELD changed,
  **models** if the news is that the CAPABILITY exists.
- A chip announced by a lab → **donanim**. The chip is the news, not the lab.
- A scientific result reached with AI → **bilim**. A result about AI itself → **kuram**.
- A deepfake scam → **olaylar**. A law about deepfakes → **politika**.
- A lawsuit over a harm → **olaylar**. A regulation or ruling that sets rules → **politika**.
- A software framework or library release → whatever it is FOR, **never** `donanim`.

### Metadata, not tags — and never a section

Determined from the feed and the URL, free and exactly right:

- **origin** — the source's country/language. This was `global`, a 298-item section that a
  content classifier agreed with **28%** of the time, because origin is not a content question.
- **format** — video or podcast. This was `multimedia`, agreement **18%**, for the same reason.

Both are useful as filters. Neither is a section, and neither should ever be asked of a model.

---

## Deriving the section

First match wins. The order encodes editorial priority: a harm outranks the rule it broke,
which outranks the hardware it ran on.

```
olaylar                      -> Ne düşünmeli?
politika                     -> Ne düşünmeli?
donanim                      -> Ne oldu?
bilim                        -> Ne işe yarıyor?
models                       -> Ne oldu?
uygulama                     -> Ne işe yarıyor?
kuram                        -> Ne düşünmeli?
```

Because the section is derived, the sections can be re-cut later — merged, split, renamed —
**without reclassifying a single article**.

---

## What was measured

| question | answer | how |
|---|---|---|
| Can a local model file by content? | **yes, 83%** | 27B vs 60 hand labels written blind |
| Which boundary is weakest? | `bilim` **57%** | same sample |
| Which are solid? | `donanim`, `politika` **100%** | same sample |
| Does 3 beat 7? | no — 85% vs 83% | collapsing both label sets |
| Would a 9B do? | **no** | 56% on `models`; systematically reads a product launch as a workplace story |
| Would embeddings do? | **no — 66%** | bge-m3 + k-NN, 5-fold, distilling the 27B |
| Is it worth optimising? | **no** | 904 articles in 231 s → **~23 s per weekly issue** |

### Why embeddings fail, specifically

They cluster by **topic**; these sections are defined by **role**. Three stories about a chip can
be `donanim` (a new accelerator), `models` (a lab announcing one) or `politika` (export controls
on it) — near-identical vocabulary, three sections. The two tags defined by *what kind of event
this is* collapse worst: `olaylar` 46%, `bilim` 47%.

Embeddings stay useful for what they are good at: cross-language dedup (already in İyiGiden at
0.80), related-article links, and "have we covered this before".

### Why the 27B and nothing smaller

It is already resident for generation, so classification costs **no model swap** — the thing that
makes mornings fragile. At ~23 s per weekly issue there is no compute problem to solve, and a
smaller model trades real accuracy for a saving nobody can perceive.

---

## Open

1. **`bilim` is the one weak boundary (57%).** It currently collides with three different things:
   AI-as-instrument results (correct), pure science with no AI involved (should not be in the
   newsletter at all — it arrives via `interestingengineering`, a feed problem), and method papers
   that are arguably `kuram`. Recommendation: define it **strictly as "AI was the instrument"**
   and let non-AI science fall out at collection.
2. **Economic and forecast stories** — "AI could raise GDP 32% by 2030" fits none of the seven
   cleanly. Currently lands in `kuram`. Needs a home or a rule.
3. **Does anything replace "Enteresan & Eğlenceli"?** ~60 pop-science items a week scatter into
   `uygulama`/`bilim` under this scheme. That may be right, or the light section may be worth
   keeping deliberately rather than by accident.
