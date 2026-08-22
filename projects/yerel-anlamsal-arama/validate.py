#!/usr/bin/env python3
"""Privacy-safe validation harness.

Run this in YOUR OWN terminal against YOUR real (confidential) folder. It prints
ONLY aggregate metrics by default — no filenames, no snippets, no document text —
so you can share the score without exposing anything.

Steps:
  1) Index your folder (local, private):
       python index.py "/path/to/folder" my.db
  2) Write a small queries file (see queries.example.json): a list of
       {"query": "...", "expect": "<substring of the right filename>"}
     'expect' is matched against the result's filename, so you can use a
     non-revealing fragment.
  3) Score:
       python validate.py my.db queries.json
     Add --show to see per-query PASS/FAIL with filenames (for your eyes only).

Metrics: P@1 (top hit correct), MRR (1/rank of the right file), P@3.
"""
from __future__ import annotations

import datetime as dt
import json
import sys


def run(db_path: str, queries_path: str, show: bool = False, top: int = 5):
    from search import search
    cases = json.loads(open(queries_path, encoding="utf-8").read())
    p1 = p3 = 0
    mrr = 0.0
    n = len(cases)
    for i, c in enumerate(cases, 1):
        q, expect = c["query"], c["expect"].lower()
        today = dt.date.fromisoformat(c["today"]) if c.get("today") else None
        out = search(q, db_path, top=top, today=today)
        names = [r["name"].lower() for r in out["results"]]
        rank = next((j + 1 for j, nm in enumerate(names) if expect in nm), 0)
        if rank == 1:
            p1 += 1
        if 1 <= rank <= 3:
            p3 += 1
        if rank:
            mrr += 1.0 / rank
        if show:
            got = out["results"][0]["name"] if out["results"] else "—"
            mark = "✓" if rank == 1 else ("~" if rank else "✗")
            print(f"  {mark} #{i:<3} rank={rank or '-'}  {q!r} -> {got}")
    print("\n================  SONUÇ  ================")
    print(f"  Sorgu sayısı : {n}")
    print(f"  P@1          : {p1}/{n} = {p1/n*100:.0f}%")
    print(f"  P@3          : {p3}/{n} = {p3/n*100:.0f}%")
    print(f"  MRR          : {mrr/n:.3f}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("kullanım: python3 validate.py <db> <queries.json> [--show]")
        raise SystemExit(1)
    run(sys.argv[1], sys.argv[2], show="--show" in sys.argv)
