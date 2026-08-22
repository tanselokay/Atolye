#!/usr/bin/env python3
"""Phase 3 (retrieval) — hybrid search over the SQLite index.

query = semantic (bge-m3 cosine)  ⊕  keyword (FTS5 bm25)  ⊕  date filter
Fused with Reciprocal Rank Fusion (RRF), then aggregated per file.

Turkish relative-time phrases ("geçen hafta", "dün", "ağustos") become a hard
date filter and are stripped from the text used for semantic/keyword search.

Usage: python search.py "geçen haftaki toplantı notları"
"""
from __future__ import annotations

import datetime as dt
import math
import re
import sys

from embed import embed_one
from store import connect, all_chunk_vectors, doc_meta
from timeparse import parse as parse_time

RRF_K = 60
DEFAULT_DB = "atolye_finder.db"


def _cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _in_range(meta: dict, rng) -> bool:
    if not rng:
        return True
    lo, hi = rng
    for key in ("modified", "created"):
        v = meta.get(key)
        if v:
            d = dt.date.fromisoformat(v[:10])
            if lo <= d <= hi:
                return True
    return False


def _fts_ranks(con, terms: list[str]) -> dict[int, int]:
    """FTS bm25 ranks for the given terms/phrases (OR-joined). Empty if none."""
    if not terms:
        return {}
    match = " OR ".join(f'"{t}"' for t in terms)
    ranks = {}
    try:
        rows = con.execute(
            "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank",
            (match,)).fetchall()
        for i, (rowid,) in enumerate(rows):
            ranks[rowid] = i
    except Exception:
        pass
    return ranks


def _exact_terms(text: str) -> list[str]:
    """Extract EXACT-INTENT signals only: quoted phrases + tokens containing a
    digit (invoice numbers, codes, years). Measured: on natural paraphrase
    queries, keyword matching on ordinary words only adds noise (semantic-only
    P@1 97% vs hybrid 87%). Keyword earns its place solely for exact lookups."""
    phrases = re.findall(r'"([^"]+)"', text)
    tokens = re.findall(r"[\w./-]+", text, flags=re.UNICODE)
    codes = [t for t in tokens if any(c.isdigit() for c in t) and len(t) >= 3]
    return phrases + codes


def search(query: str, db_path: str = DEFAULT_DB, top: int = 5,
           today: dt.date | None = None) -> list[dict]:
    con = connect(db_path)
    rng, text = parse_time(query, today=today)
    text = text or query  # if the whole query was a time phrase, fall back

    # semantic ranks (primary)
    qv = embed_one(text)
    sims = [(cid, doc_id, _cosine(qv, vec)) for cid, doc_id, vec in all_chunk_vectors(con)]
    sims.sort(key=lambda x: x[2], reverse=True)
    sem_rank = {cid: i for i, (cid, _, _) in enumerate(sims)}
    chunk_doc = {cid: doc_id for cid, doc_id, _ in sims}
    chunk_sim = {cid: s for cid, _, s in sims}

    # keyword ranks ONLY for exact-intent terms (quoted phrases / codes / numbers);
    # ordinary words are left to semantics, which measured far better on paraphrases.
    exact = _exact_terms(text)
    kw_rank = _fts_ranks(con, exact) if exact else {}

    # RRF fuse at chunk level (keyword contributes only when exact terms exist)
    fused: dict[int, float] = {}
    for cid, r in sem_rank.items():
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + r)
    for cid, r in kw_rank.items():
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + r)

    # aggregate to doc (best chunk), apply date filter
    best: dict[int, tuple[float, int]] = {}
    for cid, score in fused.items():
        doc_id = chunk_doc[cid]
        meta = doc_meta(con, doc_id)
        if not _in_range(meta, rng):
            continue
        if doc_id not in best or score > best[doc_id][0]:
            best[doc_id] = (score, cid)

    results = []
    for doc_id, (score, cid) in sorted(best.items(), key=lambda x: x[1][0], reverse=True)[:top]:
        meta = doc_meta(con, doc_id)
        snip = con.execute("SELECT text FROM chunks WHERE id=?", (cid,)).fetchone()[0]
        results.append({
            "score": round(score, 4), "sim": round(chunk_sim.get(cid, 0), 3),
            "keyword_hit": cid in kw_rank,
            "name": meta["name"], "title": meta["title"], "path": meta["path"],
            "modified": (meta["modified"] or "")[:10], "kind": meta["kind"],
            "snippet": snip[:160].replace("\n", " "),
        })
    con.close()
    return {"range": rng, "text": text, "results": results}


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "geçen haftaki toplantı notları"
    db = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DB
    out = search(q, db, today=dt.date(2026, 8, 22))
    rng = out["range"]
    print(f'Sorgu: {q!r}')
    print(f'  tarih filtresi: {rng[0]}..{rng[1]}' if rng else '  tarih filtresi: yok')
    print(f'  anlam/kelime metni: {out["text"]!r}\n')
    for i, r in enumerate(out["results"], 1):
        kw = "🔤" if r["keyword_hit"] else "  "
        print(f'  {i}. {kw} {r["name"]:<34} [{r["modified"]}] sim={r["sim"]} skor={r["score"]}')
        print(f'        {r["title"]}')
