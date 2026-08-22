#!/usr/bin/env python3
"""Build the index: folder of .docx/.pptx -> SQLite (chunks + vectors + FTS5).

Usage: python index.py <folder> [db_path]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from extract import extract, iter_files
from chunk import chunk_text
from embed import embed_batch
from store import connect, upsert_doc, clear_doc_chunks, add_chunk

DEFAULT_DB = "atolye_finder.db"


def build(folder: str, db_path: str = DEFAULT_DB) -> dict:
    folder_p = Path(folder).expanduser()
    if not folder_p.is_dir():
        raise SystemExit(f"HATA: klasör bulunamadı: {folder_p}\n"
                         f"  (tırnak içindeki ~ genişlemez; tırnaksız yazın veya tam yol verin)")
    files = list(iter_files(folder_p))
    if not files:
        raise SystemExit(f"HATA: {folder_p} altında .docx/.pptx/.xmind dosyası yok "
                         f"(alt klasörler dahil tarandı).")
    db_path = str(Path(db_path).expanduser())
    con = connect(db_path)
    n_docs = 0
    t0 = time.time()

    # pass 1: extract + chunk everything, collecting rows to embed in one batch
    rows = []  # (doc_id, unit_id, piece, embed_context)
    for f in files:
        try:
            meta, units = extract(f)
        except Exception as e:
            print(f"  ! atlandı {f.name}: {e}")
            continue
        doc_id = upsert_doc(con, meta)
        clear_doc_chunks(con, doc_id)
        for u in units:
            for piece in chunk_text(u.text):
                # prepend title so short docs carry their identity into the vector
                ctx = f"{meta.title}. {piece}" if meta.title else piece
                rows.append((doc_id, u.unit_id, piece, ctx))
        n_docs += 1
        print(f"  + {meta.name}  ({len(units)} birim)")

    # pass 2: one batched GPU embedding pass over all chunks
    print(f"\n  {len(rows)} parça gömülüyor (toplu, GPU)...")
    vecs = embed_batch([r[3] for r in rows])
    for (doc_id, unit_id, piece, _), vec in zip(rows, vecs):
        add_chunk(con, doc_id, unit_id, piece, vec)
    n_chunks = len(rows)
    con.commit()
    dt = time.time() - t0
    size = Path(db_path).stat().st_size
    con.close()
    return {"docs": n_docs, "chunks": n_chunks, "seconds": dt, "db_bytes": size}


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "../sample"
    db = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DB
    r = build(folder, db)
    print(f"\n{r['docs']} belge, {r['chunks']} parça, {r['seconds']:.1f}s, "
          f"indeks {r['db_bytes']/1024:.0f} KB -> {db}")
