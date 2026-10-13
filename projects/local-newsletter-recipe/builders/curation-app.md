# Builder prompt — the curation (review) app

> Produces a running starting skeleton you then shape — not a finished product.

---

You are helping me build a small, local **curation app** — the human-review step of a
local-AI newsletter pipeline. Its only job: let one person review AI-drafted story candidates
and decide what gets published. It is not a CMS and not public; it runs on my own machine.

Before writing any code, ask me these questions, then build to my answers:
1. What language is my newsletter in, and what language do I want the app's buttons in?
2. Where do candidate stories come from — what file/format does my pipeline produce? If I don't
   have one yet, assume one JSON file per date: a list of items, each with id, title, why, url,
   source, image, section, and optional flags.
3. Which stack — Python/FastAPI, Python/Flask, Node/Express, or your recommendation?
4. Where should it read candidates from and write the curated result to?
5. Cover-image and section controls, or just "include" + edit the text?

Then build a minimal app I can run locally with one command, following these rules — the ones
learned the hard way:

- **Never auto-publish.** Nothing ships unless I tick it in. Items start unticked.
- **Save per field, on blur.** Edit a headline or note, save that one field right away — no big
  "Save" button to forget. Show a small saved indicator.
- **Show flags loudly.** Possible duplicate, a health/medical claim to verify, a too-small image:
  a visible badge on the card, never buried.
- **Group by section** in a fixed order, with a live "X selected" counter — people unconsciously
  stop near a target size, so keep the count in view.
- **Keep state in a plain file** (the per-date JSON), inspectable, nothing locked in a database.
- **Preview and publish** buttons — and publish must clearly report whether it *actually*
  succeeded. A failed publish must never look like success.
- Plain, fast, **accessible** HTML; works on a phone; no build step.

Keep it small — a daily tool for one person, not a product. Ask your questions now.
