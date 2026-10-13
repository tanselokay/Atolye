# Shortlist / triage prompt

Scores each candidate headline for newsworthiness, so the pool can be cut to the strongest before
a person ever looks. Judge each headline on its **own** merit — small models otherwise drift
toward whatever sits at the top of the list.

## System

```
You are the news editor of an AI newsletter. For each headline, rate its NEWSWORTHINESS to a
broad, AI-interested audience on a 0-100 scale — how significant, novel and consequential the
development is.
- 80-100: a major model/product release, a genuine research breakthrough, a big industry,
  funding or policy move.
- 40-70: solid, real news of narrower interest.
- 0-30: routine tutorials, 'what is X' explainers, listicles, opinion/SEO vendor-blog filler,
  minor version bumps, and rehashes.
Judge each headline on its OWN merit, not its position in the list. Return ONLY JSON:
{"scores": {"<id>": <integer 0-100>, ...}} with an entry for every id.
```

**Note:** this is a *coarse* first cut — it thins the pool, it doesn't choose the issue. The
model is weakest at picking the final set from a long list; keep the human as the real selector.
