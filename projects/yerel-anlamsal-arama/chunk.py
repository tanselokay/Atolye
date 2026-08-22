#!/usr/bin/env python3
"""Phase 2 (chunking) — split extracted units into embed-sized pieces.

Units are already meaningful (a heading section, a slide, a table). Most fit in
one chunk; only long sections get windowed (~350 words, small overlap) so bge-m3
sees coherent context. Word count is a good-enough proxy for tokens here.
"""
from __future__ import annotations

import re

MAX_WORDS = 350
OVERLAP = 40


def _sentences(text: str) -> list[str]:
    # split on sentence enders and newlines, keep it simple + Turkish-safe
    parts = re.split(r"(?<=[.!?:])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_words: int = MAX_WORDS, overlap: int = OVERLAP) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text.strip()] if text.strip() else []
    chunks, sents, cur, n = [], _sentences(text), [], 0
    for s in sents:
        w = len(s.split())
        if n + w > max_words and cur:
            chunks.append(" ".join(cur))
            # carry an overlap tail
            tail, tn = [], 0
            for x in reversed(cur):
                tail.insert(0, x); tn += len(x.split())
                if tn >= overlap:
                    break
            cur, n = tail, tn
        cur.append(s); n += w
    if cur:
        chunks.append(" ".join(cur))
    return chunks
