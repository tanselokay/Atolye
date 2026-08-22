#!/usr/bin/env python3
# Generated with Claude Opus 4.8 (Anthropic). Review before use.
# Bu dosya Claude Opus 4.8 (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""Phase 3 (storage) — one local SQLite file: chunks + vectors + FTS5 + dates.

Zero-ops, single-file, fully local. Vectors are stored as float32 blobs and
scored by brute-force cosine in Python (fine for a personal folder; swap in
sqlite-vec only if the corpus grows to many thousands of chunks).
"""
from __future__ import annotations

import array
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS docs (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE, name TEXT, kind TEXT,
    created TEXT, modified TEXT, author TEXT, title TEXT
);
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    doc_id INTEGER REFERENCES docs(id) ON DELETE CASCADE,
    unit_id TEXT, text TEXT, vector BLOB
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
    USING fts5(text, content='chunks', content_rowid='id',
               tokenize='unicode61 remove_diacritics 2');
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(Path(db_path).expanduser()))
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SCHEMA)
    return con


def vec_to_blob(vec) -> bytes:
    return array.array("f", vec).tobytes()


def blob_to_vec(blob: bytes) -> array.array:
    a = array.array("f"); a.frombytes(blob); return a


def upsert_doc(con, meta) -> int:
    cur = con.execute(
        """INSERT INTO docs(path,name,kind,created,modified,author,title)
           VALUES(?,?,?,?,?,?,?)
           ON CONFLICT(path) DO UPDATE SET
             name=excluded.name, kind=excluded.kind, created=excluded.created,
             modified=excluded.modified, author=excluded.author, title=excluded.title
           RETURNING id""",
        (meta.path, meta.name, meta.kind,
         meta.created.isoformat() if meta.created else None,
         meta.modified.isoformat() if meta.modified else None,
         meta.author, meta.title))
    return cur.fetchone()[0]


def clear_doc_chunks(con, doc_id: int):
    ids = [r[0] for r in con.execute("SELECT id FROM chunks WHERE doc_id=?", (doc_id,))]
    con.execute("DELETE FROM chunks WHERE doc_id=?", (doc_id,))
    for cid in ids:
        con.execute("INSERT INTO chunks_fts(chunks_fts,rowid,text) VALUES('delete',?,'')", (cid,))


def add_chunk(con, doc_id: int, unit_id: str, text: str, vec) -> int:
    cur = con.execute(
        "INSERT INTO chunks(doc_id,unit_id,text,vector) VALUES(?,?,?,?)",
        (doc_id, unit_id, text, vec_to_blob(vec)))
    cid = cur.lastrowid
    con.execute("INSERT INTO chunks_fts(rowid,text) VALUES(?,?)", (cid, text))
    return cid


def all_chunk_vectors(con):
    """Yield (chunk_id, doc_id, vector) for brute-force semantic scoring."""
    for cid, doc_id, blob in con.execute("SELECT id,doc_id,vector FROM chunks"):
        yield cid, doc_id, blob_to_vec(blob)


def doc_meta(con, doc_id: int) -> dict:
    row = con.execute(
        "SELECT path,name,kind,created,modified,author,title FROM docs WHERE id=?",
        (doc_id,)).fetchone()
    keys = ("path", "name", "kind", "created", "modified", "author", "title")
    return dict(zip(keys, row))
