# Builder prompt — the publisher

> Produces a running starting skeleton you then shape — not a finished product.

---

You are helping me build the **publisher**: it turns the curated items into static web pages and
an RSS feed, then deploys them to cheap hosting. No database, no server to babysit.

Ask me first: (1) where are the curated items, and where should the built site go? (2) my hosting
— an rsync/SSH target, a static host, something else? (3) one language or bilingual? (4) site
name, author, feed title? Then build it, following:

- **Static only** — plain HTML + an RSS/Atom feed. Cache-bust each page on re-publish.
- **Accessible by default** — semantic headings, a skip link, real alt text, AA contrast, phone.
- **Link out; never re-host others' work** — hotlink or embed source media and credit it, don't
  copy articles. (Also the safe side of copyright.)
- **Deploy simply**, but **never with a blind delete** — a careless `rsync --delete` once wiped a
  whole archive. Remove remote files explicitly and deliberately.
- **Report the deploy result loudly.** A failed upload must not look like success — log it and
  alert, so "I pressed publish and left" is safe.
- Don't rebuild templates mid-publish.

Keep pages small and fast. Ask your questions now.
