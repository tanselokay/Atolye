#!/usr/bin/env python3
"""Phase 2 (embedding) — bge-m3 (multilingual) via a local Ollama.

Proven in experiments/tr-embed-ab: bge-m3 DIRECT on Turkish = 100% P@1, no
en_pivot translation needed. That's why the finder uses it.
"""
from __future__ import annotations

import json
import os
import urllib.request

OLLAMA = os.environ.get("ATOLYE_OLLAMA", "http://localhost:11434")
MODEL = os.environ.get("ATOLYE_EMBED", "bge-m3")


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def embed_one(text: str, timeout: int = 120) -> list[float]:
    req = urllib.request.Request(
        f"{OLLAMA}/api/embeddings",
        data=json.dumps({"model": MODEL, "prompt": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with _opener().open(req, timeout=timeout) as r:
        return json.loads(r.read())["embedding"]


def embed_batch(texts: list[str], batch_size: int = 64, timeout: int = 300) -> list[list[float]]:
    """Batch embedding via /api/embed (array input) — one GPU pass per batch.
    ~18x faster than one-at-a-time and saturates the GPU. Falls back to the
    single endpoint if the server is old and lacks /api/embed."""
    out: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i + batch_size]
        req = urllib.request.Request(
            f"{OLLAMA}/api/embed",
            data=json.dumps({"model": MODEL, "input": chunk}).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        try:
            with _opener().open(req, timeout=timeout) as r:
                embs = json.loads(r.read()).get("embeddings")
            if not embs or len(embs) != len(chunk):
                raise ValueError("beklenmeyen /api/embed yanıtı")
            out.extend(embs)
        except Exception:
            out.extend(embed_one(t, timeout) for t in chunk)  # graceful fallback
    return out


def embed_many(texts: list[str], timeout: int = 120) -> list[list[float]]:
    return embed_batch(texts, timeout=timeout)


if __name__ == "__main__":
    v = embed_one("geçen haftaki pazarlama toplantısı notları")
    print(f"bge-m3 via {OLLAMA}: boyut={len(v)}, ilk 3={v[:3]}")
