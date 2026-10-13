# Builder prompt — the collector

Paste the block into an AI coding assistant. It asks a few questions, then builds your collector.
> Produces a running starting skeleton you then shape — not a finished product.

---

You are helping me build the **collector** for a local-AI newsletter: it gathers articles from
many sources into one place, every day, so a model can later shortlist them. Not public; runs on
my machine.

Ask me first: (1) which languages and which sources — RSS feeds, site searches, a few channels?
(2) where should it store what it finds? (3) when should it run? Then build it, following:

- **Gather wide, prune later** — don't over-filter at collection; surface a broad pool.
- **Dedupe by canonical URL** as things come in (strip tracking params first).
- **One slow or broken source must never kill the run** — isolate each source, time it out, keep
  going. A dropped source should shrink the pool, not empty it.
- **Record provenance** — keep where each item came from and when first seen.
- **Many languages are fine** — tag each item's language; don't translate here.
- Write a simple per-day store (JSON or SQLite) that the next step reads.

Keep it boring and reliable. Ask your questions now.
