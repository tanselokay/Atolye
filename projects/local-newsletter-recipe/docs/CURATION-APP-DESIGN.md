# DevWatch Curation App — Design (for review)

## Goal
A small **local web app** to curate the daily newsletter: review auto-drafted
Turkish titles/blurbs for the day's candidate articles (from **both** the
DEVONagent and DEVONthink tracks), edit them, choose which go in, and **publish**
to demle.me (+ optional email). Every edit is captured as fine-tuning data.

Guiding principle: **automation drafts, you approve, then it ships.** The grounded
120B output is a *draft*, never published unseen — which is the answer to the
hallucination risk we hit (embellished specifics, "AçıkAI", etc.).

## Why local + reuse
- Runs on your Mac (localhost), no new external hosting, no auth headaches.
- Reuses the existing pipeline: `build_issue` / `generate_grounded_meta` for
  drafts, the light template for rendering, `publish_demle` for deploy, the
  osascript mailer for email.

## Stack (minimal, no build step)
- **Backend:** FastAPI in the existing `.venv`, served by uvicorn on
  `localhost:8765`. (One new dep: fastapi+uvicorn.)
- **Frontend:** a single static HTML page + vanilla JS — no React/build. Styled
  with the light newsletter theme so the editor *looks like* the output.
- **Storage:** `data/curation/<date>.json` (drafts + your edits + include/order
  state). Corpus in `data/mt_corpus/<pillar>.jsonl`.

## Data flow
1. **Prepare drafts** (heavy, once/day or on-demand button): pull today's
   candidates from both tracks, run `generate_grounded_meta` (120B) for a
   content-faithful Turkish title + blurb, fetch images → cache in
   `data/curation/<date>.json`.
2. **Curate** (browser): load the draft; edit title/blurb inline, toggle
   include/exclude, reorder, optionally reassign pillar.
3. **Publish**: render the curated items into the light template → `publish_demle`
   (+ optional email) → append every edited pair to the corpus.

## Screens
- **Issue editor:** header (date, item count, Prepare / Preview / Publish / Email
  buttons). Pillar sections. Each candidate is an editable card: image, source
  link, score, **source badge** (devonagent / devonthink), editable Turkish
  **title**, editable **blurb**, include checkbox, drag handle.
- **Preview:** the real newsletter HTML in an iframe.
- **(later) Corpus stats:** pairs collected per pillar toward a fine-tune target.

## API
- `POST /api/prepare/{date}` — generate/refresh drafts (kicks off ground_meta).
- `GET  /api/issue/{date}` — current draft/curated state.
- `PUT  /api/item/{date}/{item_id}` — save edited title/blurb/include/order/pillar.
- `POST /api/item/{date}/{item_id}/redraft` — regenerate one item's draft.
- `POST /api/publish/{date}` — render + `publish_demle` (+ `email=true`). Returns URL.
- `GET  /preview/{date}` — rendered HTML.

## Corpus capture (fine-tune fuel)
On publish, for each item where you changed the text, append to
`data/mt_corpus/<pillar>.jsonl`:
```json
{"item_id":…, "url":"…", "source":"devonthink", "pillar":"pulse", "date":"…",
 "en_title":"…", "draft_title_tr":"…", "final_title_tr":"…",
 "draft_why_tr":"…", "final_why_tr":"…", "changed_title":true, "changed_why":true}
```

## Phases
- **MVP (Phase 1):** list today's devonthink+devonagent candidates with drafts,
  edit title/blurb, include/exclude, Publish to demle.me, corpus capture.
- **Phase 2:** reorder + pillar reassign, live preview iframe, email send,
  per-item "redraft" button.
- **Phase 3:** corpus stats dashboard + JSONL export for QLoRA.

## Decisions (locked 2026-07-19)
1. **Sourcing — POOL BOTH into one issue.** DEVONagent + DEVONthink candidates
   appear together in one curated demle.me issue, each with a **source badge**.
   Both tracks map into the pillar taxonomy already; **dedupe by final URL** so an
   item collected on both tracks appears once (keep the higher score / prefer
   devonthink). Implementation: pull candidates with no source filter, merge, dedupe.
2. **Draft timing — ON-DEMAND.** A **Prepare** button runs `generate_grounded_meta`
   (120B) over the day's candidates when you open the app (~1–2 min; show
   progress). No ground_meta cost added to the 07:30 pipeline.
3. **Publish — demle.me ONLY** for MVP. Email deferred to Phase 2 (the osascript
   mailer is ready to wire in later).
4. **Reach — LAN (phone too).** uvicorn binds `0.0.0.0:8765`; open from the Mac or
   `http://<mac-LAN-ip>:8765` on your phone. Home LAN only (not public). Add a
   simple shared-secret token in the URL/header since other devices can reach it.

## Notes from decisions
- Because sources are pooled, the digest (devonagent → email @09:00) is unchanged
  and separate; the app is a *third* consumer that can pull devonagent items too.
- Publishing an **edited** item set means the renderer takes the curated items
  directly (from `data/curation/<date>.json`), not a fresh `build_issue`. So the
  render step is refactored to accept explicit items.
