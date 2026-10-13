# A local-first newsletter engine — the recipe

> ⚠ **Work in progress.** A snapshot of how [demle.me](https://demle.me) is made, not a finished
> product. It changes as new needs appear. Treat it as a blueprint, not a spec.

This is not a one-click clone of demle.me. It's the **method** — the prompts, the content
taxonomy, the source list, the design notes, and a set of **builder prompts** — so you can build
your own small, honest, local-first publication, shaped around your own topic, language and
hardware.

It's deliberately the *lighter* release: the ideas and the ingredients, not a turnkey pipeline.
demle.me is tuned to one person's setup, so copying it line-for-line wouldn't fit you anyway. The
part that transfers is the part worth sharing: **how to make a machine draft, and a human decide.**

## The idea in one line

Local AI reads a flood of sources and drafts; a human makes every choice that reaches a reader;
the result is published openly and cheaply. No cloud AI, no per-article cost, no black box.

## Build your own — six steps

Decisions, not commands. Each step points to material here you can borrow, and to a **builder
prompt** you can paste into your own AI assistant to generate that part for your setup.

**1. Pick an engine you own.** A local model that runs on your machine. → `docs/MODELS.md`

**2. Point it at your sources.** Decide what to watch — feeds, searches, a few channels. Start
broad. → `recipe/` (my list, as an example) · build it → `builders/collector.md`

**3. Let the model read, shortlist and draft.** The prompts are the real craft.
→ `prompts/` · `docs/TAXONOMY.md` · build it → `builders/drafting.md`

**4. Put a human in the loop — always.** Never auto-publish. A small daily step where you pick,
fix and check. → `docs/CURATION-APP-DESIGN.md` (design notes; build your own) · build it →
`builders/curation-app.md`

**5. Publish simply.** Static pages + an RSS feed on cheap hosting. → `docs/ARCHITECTURE.md` ·
build it → `builders/publisher.md`

**6. Keep it healthy.** Back up, repair dead links (archive.org), and — the lesson that cost me
the most — add a check that answers *"did it actually publish?"* → build it → `builders/upkeep.md`

## Have your AI build it

Each part has a **builder prompt** in `builders/`. Paste one into an AI coding assistant; it asks
you a few questions, then generates *your* version with the hard-won rules baked in. Build in
order — collector → drafting → curation → publisher → upkeep — each assumes the previous output.
What you get is a running starting skeleton you then shape, not a finished demle.me.

## A signature in the light

Every cover is generated in **morning light** — soft, golden, the first light of day. Not a
default: my name, *Tansel*, means the light of daybreak, so the covers carry it (one line in
`prompts/03-cover.md`). It's the point of building your own instead of using someone else's tool:
**an automated system can still hold a personal mark.** Give yours a signature that's yours.

## What's in this repo

- **`builders/`** — a prompt per pipeline part; paste into your AI to build your own version.
- **`prompts/`** — the real prompts the models run (headline, critique, cover).
- **`docs/`** — architecture, principles, the content taxonomy (with its measured dead-ends),
  curation-app design notes, and a pipeline-decoupling design doc.
- **`recipe/`** — the source list and topic/glossary config, as a starting example.

What's *not* here: the full runnable pipeline, and anything tied to my own servers.

## Principles

- The machine drafts; a human decides.
- All AI runs locally — private, no cloud, no cost per article.
- Honest: a page says what the machine wrote and what wasn't reviewed.
- Built to be accessible to everyone.
- Links out and credits others; never re-hosts their work.

This method was built with **Claude** as an AI coding partner. The articles are drafted by
**open-weight models running locally** — a different AI doing a different job. Every editorial
choice is the human's.

## License & credit

- Code: **MIT** (`LICENSE`). Prompts, docs, builders, recipe: **CC-BY-4.0** (`LICENSE-DOCS.md`).
- If you build on this, please credit:
  **by Tansel Okay ([demle.me](https://demle.me)), built with Claude as an AI coding partner.**

Build something that's yours. That's the whole point.
