# Builder prompt — the upkeep jobs

> Produces running starting skeletons you then shape — not a finished product.

---

You are helping me build the **upkeep jobs** — scheduled tasks that keep a small publication
alive. They run on their own and alert me only when something is actually wrong.

Ask me first: (1) where's my site and where do backups go? (2) an email (or channel) for alerts?
(3) what schedule suits me? Then build these, each a small independent job:

- **Dead-link repair** — check outbound links; when one dies, swap it for an archive.org snapshot
  (Save Page Now), so old issues don't rot.
- **Backup** — a nightly snapshot of the published site.
- **Publish verification** — after a deploy, compare the live site to the local build; email only
  on a mismatch or a broken internal link.
- **Source vetting** — periodically measure which sources actually earn their place (precision,
  not volume) and flag the noisy ones to prune.
- **"Did it actually publish?"** — the check that catches the silent failure: confirm the newest
  issue is really live, alert if not.

Quiet by design: no news is good news. Ask your questions now.
