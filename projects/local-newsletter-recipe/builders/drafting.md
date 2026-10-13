# Builder prompt — the drafting step

> Produces a running starting skeleton you then shape — not a finished product.

---

You are helping me build the **drafting step**: given the day's collected articles, a **local**
model shortlists the strongest and writes, for each, a faithful headline and a two-sentence "why
it matters" in my newsletter's language. Output is the file my review app opens.

Ask me first: (1) my newsletter's language? (2) which local model and endpoint do I run (e.g.
Ollama on localhost)? (3) any topics to always exclude? (4) a target number of stories per issue?
Then build it, following these rules — the faithfulness ones are non-negotiable:

- **Never invent a fact that isn't in the source.** Keep every number, name and place. A thinner
  source gets a thinner sentence, never a fabricated one.
- **Faithful headline, not the publisher's clickbait** — state what happened, no teasing.
- **Flag near-duplicates, don't silently drop them** — group similar stories (embeddings) and
  mark them for the human to choose.
- **Apply my editorial exclusions** (configurable) and low-value-source filtering.
- **Auto-include the top N by score**; leave the rest in the pool as un-ticked candidates.
- Keep a small **glossary** so recurring terms translate consistently.
- Write the per-date JSON: items with id, title, why, url, source, image, section, flags.

The prompts you write for the model are the real craft — make them explicit and editable. See
`prompts/` in this repo for the real ones I use (headline, critique, translation, cover). Ask now.
