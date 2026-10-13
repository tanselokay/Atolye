# Decoupling the newsletter paths, keeping publish shared

**Status:** design, for reaction. Nothing moved yet.
**Written:** 2026-10-06. **Re-verified against `76c4dc9` (838 tests): 2026-10-08** — line refs
updated; §7 corrected: two render-level isolation tests already exist, and the full-publish test
would **fail today** on one shared write (§7.1).

> Your ask (2026-10-06): *"I agree with the common services (publish) but we should decouple
> newsletter paths as much as possible, otherwise these are two newsletters and if I add 4–5 it may
> become unmanageable."* And: *"remove buttons which do not work for me ... if me pushing a fake
> button would tamper with another newsletter that would be a disaster."*

This doc proposes the **shape**, not the diff. Read §3 (the one real move), §4 (the test of the
design), and §6–7 (the two guarantees you asked for). The rest is there so you can see what I am
*not* changing and why.

---

## 1 · The question

You run two titles today — AiPulse (No.77) and İyi Giden Şeyler (No.7) — and plan 4–5. They already
share one renderer, one curation app, one publish path, one deploy. The worry is that "share
everything" collapses into "two newsletters tangled in one codebase," and the cost of a fifth title
grows with every title before it.

The design has exactly one job to answer: **does adding title #5 touch the core, or not?**

If #5 is *a new pipeline module + a config entry, and nothing in the shared code changes*, the
architecture scales. If #5 means editing `store.py`, `app.py`, or `render.py`, it doesn't — it just
looks shared.

## 2 · What is already decoupled (so we don't re-litigate it)

Most of the per-title surface is already a clean seam, and it works. Worth stating plainly so we
only spend effort on the part that isn't:

- **The renderer is decoupled.** `render.py` renders whatever `publication.current()` says, via a
  `ContextVar` set by `using()` ([publication.py:289](src/devwatch/curation/publication.py)). Chrome,
  wordmark, tagline, feeds, pillars, theme, language-storage key, English twins — all read from the
  `Publication`. `test_render_uses_the_current_publication_everywhere`
  ([test_publication.py:145](tests/test_publication.py)) already proves `/aipulse/` appears nowhere in
  a rendered İyiGiden page.
- **The paths are decoupled.** `store.save/load`, issue numbering, `published_issues`, asset URLs all
  take a `Publication` and default to AiPulse. `test_a_second_publication_writes_only_to_its_own_directory`
  and the issue-numbering test ([test_publication.py:45,58](tests/test_publication.py)) hold.
- **The config seam exists.** `config/publications.json` + the built-in `AIPULSE`; a title is a
  registry entry today ([publication.py:207](src/devwatch/curation/publication.py)).

So the `Publication` object and the render/store layers are **not** the coupling. One thing is.

## 3 · The one coupling that remains: `prepare()` is a pipeline wearing a shared-service costume

`store.prepare()` ([store.py:396](src/devwatch/curation/store.py)) is described as a store helper, but
read what it does: it walks AiPulse's `SOURCES`, reads AiPulse's DEVONthink `ANALYSIS_DIR`, runs
AiPulse's dedup (mxbai), AiPulse's arms filter, AiPulse's target-size logic — **that is AiPulse's
candidate-production pipeline.** It lives in `store.py`, the shared module, and the curation app wires
it to the Hazırla button for *every* title ([app.py:72](src/devwatch/curation/app.py),
`_prepare_worker`).

It already knows this is wrong. It opens with a hard guard:

```python
_p = _pub(None)
if _p is not AIPULSE:
    raise RuntimeError(f"prepare() reads {ANALYSIS_DIR}, which belongs to {AIPULSE.title}...")
```
— [store.py:410](src/devwatch/curation/store.py). That guard is the scar from 2026-09-20, when pressing
Hazırla on İyiGiden filled its curation file with AiPulse stories, pre-ticked, one click from
shipping. The guard turned a data-corruption bug into a loud error. **That loud error is the "fake
button" you want gone** — on :8766, Hazırla raises every single time, by design.

Meanwhile İyiGiden's *real* pipeline already exists — but as a **script run out-of-band**:
`scripts/iyigiden_prepare` ([scripts/iyigiden_prepare](scripts/iyigiden_prepare)). It does the same
job (produce candidates → write the curation JSON via `store.save(date, data, pub)`), with its own
feeds, its own cross-language dedup (bge-m3, measured at 0.80), its own both-editions writer. It is a
complete, well-reasoned pipeline. It is just not reachable from the app.

So the asymmetry is the whole problem:

| | AiPulse | İyiGiden |
|---|---|---|
| Pipeline lives in | `store.prepare()` (shared module) | `scripts/iyigiden_prepare` (out-of-band script) |
| Reachable from app's Hazırla | yes (it's the default) | no — guard raises |
| Title #5 would | have to edit `store.prepare` or add another branch | copy a script |

**The move:** make "how candidates are produced" a *named, pluggable pipeline* that the
`Publication` declares and the app dispatches to. Then AiPulse's `prepare` and İyiGiden's script are
two implementations of one interface, neither of them privileged, and #5 is a third file.

## 4 · The proposed shape

```
SHARED CORE   render issue + haber + EN twins · feeds · sitemap · covers · publish · deploy
              (store read/write, issue numbering, app routes — title-agnostic)
   ▲
   │  INTERFACE = the curation JSON  +  the Publication
   ▼
PER-TITLE     a pipeline: "how this title's candidates are produced"
              aipulse · iyigiden · weekly · #5 · #6
```

### 4.1 The interface is already a fact, not a new invention

Every pipeline today already ends the same way: **it writes the curation JSON** (`store.save(date,
data, pub)`), and everything downstream — the app, the renderer, the feed, publish, deploy — operates
on that JSON + the `Publication`. AiPulse's `prepare` writes it; İyiGiden's script writes it. The
interface between "per-title" and "shared" is therefore **the curation JSON, parameterised by the
Publication.** We don't design it; we name it and stop crossing it.

The one rule that makes the seam real: **a pipeline reads whatever it wants (its own feeds, its own
DB, its own models) and writes *only* through `store.save(..., pub)`.** No pipeline reads another
title's inputs; no core module reads any title's inputs.

### 4.2 `Publication` grows one field

```python
pipeline: str = "aipulse"   # which candidate-producer runs for this title
```

`AIPULSE` keeps the default, so nothing changes for it. İyiGiden's config entry gains
`"pipeline": "iyigiden"`. (This is the same pattern as `kritik`, `pillars`, `feed_granularity` —
a declarative capability on the title, read by the core.)

### 4.3 A pipeline is a module with one entry point

A thin protocol — not a framework. Two methods, because the app already calls two things
(`prepare` and `merge_prepare`):

```python
# devwatch/curation/pipelines/__init__.py
class Pipeline(Protocol):
    def prepare(self, date: str, pub: Publication, *, fresh: bool) -> dict: ...
    #   produce candidates for `date`, write via store.save(date, data, pub), return the data.
    #   `fresh=True` means rebuild from scratch; False means merge into an existing day.

def get(name: str) -> Pipeline | None:   # None = this title has no app-driven pipeline
```

- `pipelines/aipulse.py` ← the body of today's `store.prepare` / `merge_prepare`, moved verbatim.
  The DEVONthink/SOURCES read, the mxbai dedup, the arms filter, the target logic — all of it leaves
  `store.py` and lands here. **`store.py` goes back to being storage.**
- `pipelines/iyigiden.py` ← the logic from `scripts/iyigiden_prepare`, lifted into a module. The
  script becomes a 5-line CLI wrapper over it (so the launchd job and manual runs keep working),
  *and* the app can now call the same code.
- `pipelines/weekly.py`, `pipelines/<#5>.py` ← later, same shape.

### 4.4 The app dispatches instead of hardcoding

`_prepare_worker` ([app.py:61](src/devwatch/curation/app.py)) stops calling `store.prepare` directly:

```python
pipe = pipelines.get(PUB.pipeline)
if pipe is None:
    # title has no app-driven producer — the button isn't shown (see §6), so we never get here
    return
pipe.prepare(date, PUB, fresh=fresh)
```

That's the entire structural change on the app side. The publish route, cover route, preview,
feeds, deploy — all untouched, because they already operate on the JSON + Publication.

### 4.5 The test of the design, walked through

**Add title #5 (say a monthly "Derin" long-read digest):**

1. `pipelines/derin.py` — write `prepare()`: pull its candidates however it likes, `store.save`.
2. `config/publications.json` — one entry: `key`, `title`, `base`, dirs, `port`, `"pipeline":"derin"`,
   `kritik`, `pillars`, theme.

That's it. `store.py`, `render.py`, `app.py`, `cover_art.py`, the feed builder, the sitemap, deploy —
**none open.** If, while doing #5, I find myself editing any of those, the seam leaked and this design
failed. That is the acceptance criterion, and it's falsifiable.

## 5 · What stays shared — on purpose, and it pays

Sharing is not the problem; *mislabelled* sharing is. These stay in the core and every title benefits
from each fix exactly once:

- **Rendering** (issue, haber, English twins, Kritik pages) — the renderer is already title-aware.
- **Publish** — numbering, cover JPEG + responsive WebP, image localization, feed, sitemap, deploy.
- **Covers** — generation + judge; already reads `current()`.
- **The curation app shell** — one app binary, `DEVWATCH_PUBLICATION=<key>` per process.

Evidence this is the right call: every İyiGiden fix this autumn also improved AiPulse (shared
renderer, shared publish). And — said honestly — **separating the titles would not have prevented a
single one of this week's seven bugs.** Every one was a *default or hardcoded `/aipulse/` string*
(`cover_art` srcset, `images.py`, archive page…), and a fork would have *carried those strings into
the copy*. The fix for those is §7, not a split.

## 6 · Fake buttons: the app should tell you what a title can't do

Today the curation app's buttons are **static HTML** ([app.py:1000–1021](src/devwatch/curation/app.py)) —
every title shows every button, and the ones it can't use either error (Hazırla on :8766) or fail
silently. You asked for two things: hide the dead ones, and **guarantee a dead button can never touch
another title.**

### 6.1 The capabilities seam

The app already knows each title's capabilities — they're declared on the `Publication`:
`kritik`, `pillars`, `pipeline`, plus whether a cover generator is installed. Expose them to the
frontend (a small `/api/capabilities` or an inlined JSON blob at page render) and gate each button:

| Button | Shown when |
|---|---|
| Hazırla / Yenile / ⟲ Sıfırdan | `pipelines.get(PUB.pipeline) is not None` |
| 🎨 Kapak üret / 🖼 8 alternatif | cover generator available for this host |
| ⇄ Konuları karıştır (weave) | `len(PUB.pillars) > 1` |
| 🎬 Keşfet (video) | title has a video lane |
| Yayınla / Önizleme | always (every title publishes) |

İyiGiden's Hazırla, once its pipeline is a module (§4.3), becomes **real** — it's no longer a fake
button to hide, it starts working. The weekly/long-read titles whose candidates come from a selection
UI rather than a producer would hide Hazırla instead. Either way: **a button is visible iff it works.**

Partly a gap, not yet a fact: `kritik` and `pillars` exist on `Publication`; a **video lane** and
**cover generation** are not declared anywhere, so the app can't read them yet. Add them once, now,
as fields with AiPulse's values as defaults (`video: bool`, `covers: "flux" | "photo-only"`), so
title #5 *sets values* in its config entry and never adds a field. A capability that only exists
as an `if PUB.key == …` in the app is the same leak §4.5 forbids.

### 6.2 The disaster guarantee is §7's isolation test, not button-hiding

Hiding a button is cosmetic. The thing you actually fear — *"pushing a fake button tampers with
another newsletter"* — is prevented not by the UI but by the **isolation test** (§7.1): a title's
publish/prepare writes *only* inside its own `curation_dir` / `site_dir`. Button-hiding stops you
*reaching* a broken action; the isolation test guarantees that even if you did, the blast radius is
one title's own directory. We want both; the test is the real guarantee.

### 6.3 Same principle, one more case: the WebP cover silent empty share card

Grouped here because it's the same defect class — *the app should tell you what it can't do.* When a
title's cover photo is a **WebP**, the share card comes out empty — and that part is deliberate:
`_share_image` ([render.py:1396](src/devwatch/curation/render.py), check at :1412) drops a WebP
`og:image` because the platforms fetch it (200) and then show no picture. Measured — JPG and PNG are fine (4
of 7 İyiGiden issues led with an original photo), WebP is the only format that breaks. No.7 hit it;
you chose not to share, so it's closed for that issue. Re-hosting as JPG is out (FSEK). **The defect
is the silence** — the drop happens at render time, after you've committed. Fix: the curation
window calls the same `_share_image` test on the item marked as cover and warns — *"bu kapak görseli paylaşım kartında görünmeyecek"* —
so it's a choice before publishing, not a discovery after. Same work, same place as the button gating:
the app surfacing a limit instead of hiding it.

## 7 · The two isolation tests you asked for

**Correction to the 10-06 draft:** both exist already, at **render** level —
`test_no_page_of_another_title_ever_says_aipulse` ([test_publication.py:451](tests/test_publication.py))
renders issue, haber, archive and both feeds for another title and greps for "AiPulse" (site menu
stripped); `test_rendering_one_title_never_writes_into_anothers_directory` (:499) proves an archive
render leaves the host title's folder untouched. They earned their keep (the CSS-comment leak, the
misplaced plate). What neither does is run **a publish**, and the publish is where the writes are:
`cover_art.write_responsive`, `pillar_art.write_emblems`, `feed.write_feeds`, the site root,
`capture_corpus`. So the work is not "write two tests" — it is **lift both from render to publish.**

### 7.0 What makes that hard today: publish is not a function

Publish is a ~200-line HTTP route, `publish()` at [app.py:662](src/devwatch/curation/app.py), that
reads the module-level `PUB`/`PUBLISH_ROOT`, calls the models (Kritik, EN pivot, alt text), and ends
in `_deploy_and_alert` (rsync). A test can only reach it through a TestClient with every model and
the deploy stubbed — brittle, and it would test the stubs as much as the paths.

**Proposal:** move the body into the core as `publish_issue(date, pub, *, deploy=True) -> Report`;
the route becomes validation + a call. That is also the honest shape of "publish stays shared" —
today the shared service is a route in the app module. The tests call `publish_issue(..., deploy=False)`
with the model stages monkeypatched to no-ops, which is fine because the model stages write only to
the curation JSON (already scoped, `store.save(..., pub)`).

### 7.1 A publish writes nothing outside an allowlist

The ask was "nothing outside its own `site_dir`". Literally, that's false **by design**: every
publish regenerates the shared site root, because the front page lists all titles. So the test is an
explicit allowlist, and every entry is a decision you can see:

| Write root | Whose | Status |
|---|---|---|
| `pub.site_dir/**`, `pub.curation_dir/**` | the title's own | allowed |
| `demle.me/index.html`, `sitemap.xml`, site feeds, Atölye feeds | site root, shared on purpose | allowed |
| `demle.me/assets/pillars/` (`write_emblems`) | shared emblem set | allowed — but should key on the title's pillars, check |
| **`data/mt_corpus/<pillar>.jsonl`** (`store.capture_corpus`, [store.py:29](src/devwatch/curation/store.py)) | **unscoped** | **fails today** |

Mechanism: point every root at `tmp_path`, snapshot (path → hash) the whole tree, run an İyiGiden
`publish_issue`, diff. Assert every created/changed path matches the allowlist, and that the AiPulse
subtree is byte-identical.

**The failing row is real:** every İyiGiden publish appends its stories to the same MT-corpus files
AiPulse writes, keyed only by pillar name. Harmless for the site, but it's exactly the
"pushing a button on one title tampers with another's data" case, and nobody would see it by
inspection. That is the test paying for itself before it is merged. (Fix is one line — the corpus
path takes `pub` — but it's your call whether the corpus should be per title or deliberately pooled;
see §9.)

### 7.2 `/aipulse/` appears nowhere in another title's output

> After the same İyiGiden `publish_issue`, grep **every file it created** (not a list of page types)
> for `/aipulse/` and `AiPulse`, with the one sanctioned exception — the `<nav class="sitenav">` menu
> that links sister titles on purpose — stripped, as the render test already does.

Grepping the produced tree instead of named renders is the point: it covers what the render test
cannot enumerate — `cover-*.webp` `<source srcset>` (the 10-05 bug), `cover.json`, Kritik pages,
English twins, the feed. Generalise it over the registry: for **every** title `t`, no other title's
`base` appears in `t`'s output. With 5 titles that's 20 pairs from one loop, and title #5 is covered
the day its config entry lands.

Known hardcodes this would flag the moment they reach a publish (today they don't):
`images.py:88` (`is_local`) and `images.py:176` write `/aipulse/` URLs, but `localize_images` is
called only by `scripts/aipulse_backfill_images` since re-hosting was dropped — **dormant, not live**
(the 10-06 note calling it live was wrong). The 6 `out_root=Path("demle.me/aipulse")` defaults in
`cover_art.py` are the live risk: any call that forgets `out_root` writes AiPulse's folder.

## 8 · Order of work (≈2 days), and the honest caveats

Proposed order — each step independently shippable, lowest-risk first:

1. **Capabilities + button gating** (§6.1) and the **WebP curation warning** (§6.3). Pure additive,
   no core change, immediate relief: no more fake buttons.
2. **Extract `publish_issue`** (§7.0) and the **two publish-level tests** (§7.1–7.2). 7.1 fails on
   `capture_corpus` until you decide §9 Q5; everything else should pass and then locks in before
   any pipeline code moves.
3. **Extract pipelines** (§4): move `store.prepare`/`merge_prepare` body → `pipelines/aipulse.py`;
   lift `iyigiden_prepare` logic → `pipelines/iyigiden.py` (script becomes a wrapper); add
   `Publication.pipeline`; app dispatches. İyiGiden's Hazırla becomes real.
4. **Delete the remaining AiPulse defaults** — the 6 `out_root=Path("demle.me/aipulse")` defaults in
   `cover_art.py`, `images.py:88/176`'s hardcoded `/aipulse/` (dormant), and `store.CURATION_DIR` as a module
   constant — now that the tests in step 2 will catch any regression.

Caveats, stated plainly:

- **This would not have prevented this week's seven bugs** — all were default/hardcoded strings a
  fork would have copied. The guard against *that* class is step 2+4, not the pipeline split.
- **Step 4 is the riskiest** and the least urgent. `store.CURATION_DIR` is monkeypatched by the
  rerender scripts and their tests ([publication.py:221](src/devwatch/curation/publication.py) has a
  comment-load of why `is AIPULSE` matters). Do it last, behind the isolation tests, or defer it.
- **`iyigiden_prepare` is 400 lines of earned reasoning** (cross-language dedup thresholds measured
  on real pools, the cluster-after-Turkish fix). Lifting it to a module must be a *move*, not a
  rewrite — byte-identical logic, verified by its existing tests (`test_iyigiden_*`).

## 9 · Open questions for you

1. **Pipeline granularity.** One `prepare(fresh=…)` entry point (§4.3), or keep `prepare` /
   `merge_prepare` as two protocol methods mirroring today's app calls? (I lean to one with a flag —
   fewer things for #5 to implement.)
2. **Titles with no producer.** Weekly gazette selects from AiPulse's *published* archive
   ([[weekly-gazette-plan]]) — its "pipeline" is a selection UI, not a candidate producer. Is that a
   `pipeline=None` (hide Hazırla, §6.1), or a distinct pipeline that reads the archive? I'd model it
   as a real pipeline that reads published issues, so the seam stays uniform.
3. **Step 4 scope.** Delete the AiPulse defaults now (behind the new tests), or leave them as
   harmless fallbacks and only forbid them via the isolation test? The defaults aren't hurting once
   §7.2 guarantees they never reach another title's output.
4. **How many titles, really?** You said 4–5. If it's truly ≤5 and hand-built, the pipeline protocol
   is justified. If some future titles are near-identical variants, we'd want a *config-only*
   pipeline (declare feeds + models, no code) as a fifth pipeline kind. Worth it now, or when a
   variant actually appears?
5. **Shared MT corpus.** `capture_corpus` pools every title's stories into `data/mt_corpus/`. Per
   title (`data/<key>/mt_corpus/`, my default — the İyiGiden register is not AiPulse's), or pooled on
   purpose (then it goes on the §7.1 allowlist as a named exception)?
6. **`publish_issue` extraction.** It's a move of the route body, not a rewrite, but it is the one
   piece of §7 that touches the core. OK to do it in step 2, before the pipelines move?
