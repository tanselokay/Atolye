#!/usr/bin/env python3
"""Phase 1 — extraction.

Pull readable text + core metadata out of Microsoft .docx and .pptx files.
No OCR, no PDF: if a document is a scanned image with no text layer, it yields
nothing here (that is an honest limit, not a bug).

Two levels of output per file:
  * DocMeta   — one per file: path, kind, dates, author, title.
  * Unit list — the text broken into meaningful pieces:
      docx -> one unit per heading-delimited section (+ one per table)
      pptx -> one unit per slide (title + body + speaker notes)

Chunking (Phase 2) refines these further; here we only preserve structure.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import docx
from pptx import Presentation


@dataclass
class DocMeta:
    path: str
    name: str
    kind: str                    # "docx" | "pptx"
    created: dt.datetime | None
    modified: dt.datetime | None
    author: str | None
    title: str | None


@dataclass
class Unit:
    """One structural piece of a document, before chunking."""
    unit_type: str               # "section" | "table" | "slide"
    unit_id: str                 # human-readable locator, e.g. "Bölüm: Bütçe" / "Slayt 3"
    heading: str                 # the heading/title, if any ("" otherwise)
    text: str
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------- metadata ---
def _fs_dates(p: Path) -> tuple[dt.datetime, dt.datetime]:
    st = p.stat()
    # birthtime exists on macOS; fall back to ctime elsewhere.
    created = getattr(st, "st_birthtime", st.st_ctime)
    return (dt.datetime.fromtimestamp(created), dt.datetime.fromtimestamp(st.st_mtime))


def _core_meta(core, p: Path, kind: str) -> DocMeta:
    """Prefer OPC core.xml dates; fall back to filesystem when empty."""
    fs_created, fs_modified = _fs_dates(p)
    created = getattr(core, "created", None) or fs_created
    modified = getattr(core, "modified", None) or fs_modified
    author = (getattr(core, "author", "") or "").strip() or None
    title = (getattr(core, "title", "") or "").strip() or None
    return DocMeta(str(p), p.name, kind, created, modified, author, title)


# -------------------------------------------------------------------- docx ---
def _is_heading(paragraph) -> bool:
    style = (paragraph.style.name or "") if paragraph.style else ""
    return style.startswith("Heading") or style in ("Title", "Subtitle")


def _table_text(table) -> str:
    rows = []
    for row in table.rows:
        cells = [c.text.strip() for c in row.cells]
        # collapse repeated merged-cell text on a row
        deduped, prev = [], None
        for c in cells:
            if c != prev:
                deduped.append(c)
            prev = c
        rows.append(" | ".join(deduped))
    return "\n".join(r for r in rows if r.strip(" |"))


def extract_docx(p: Path) -> tuple[DocMeta, list[Unit]]:
    d = docx.Document(str(p))
    meta = _core_meta(d.core_properties, p, "docx")

    units: list[Unit] = []
    cur_heading = ""
    buf: list[str] = []

    def flush():
        body = "\n".join(x for x in buf if x.strip())
        if cur_heading or body.strip():
            uid = f"Bölüm: {cur_heading}" if cur_heading else "Bölüm: (başlıksız)"
            units.append(Unit("section", uid, cur_heading,
                              (cur_heading + "\n" + body).strip() if cur_heading else body))

    for para in d.paragraphs:
        txt = para.text.strip()
        if _is_heading(para):
            flush()
            cur_heading = txt
            buf = []
        elif txt:
            buf.append(txt)
    flush()

    for i, table in enumerate(d.tables, 1):
        ttext = _table_text(table)
        if ttext.strip():
            units.append(Unit("table", f"Tablo {i}", "", ttext))

    return meta, units


# -------------------------------------------------------------------- pptx ---
def _shape_text(shape) -> str:
    if shape.has_text_frame:
        return "\n".join(p.text for p in shape.text_frame.paragraphs if p.text.strip())
    return ""


def extract_pptx(p: Path) -> tuple[DocMeta, list[Unit]]:
    prs = Presentation(str(p))
    meta = _core_meta(prs.core_properties, p, "pptx")

    units: list[Unit] = []
    for i, slide in enumerate(prs.slides, 1):
        title = ""
        if slide.shapes.title and slide.shapes.title.text.strip():
            title = slide.shapes.title.text.strip()

        parts: list[str] = []
        for shape in slide.shapes:
            if shape == slide.shapes.title:
                continue
            t = _shape_text(shape)
            if t.strip():
                parts.append(t)

        notes = ""
        if slide.has_notes_slide:
            notes = (slide.notes_slide.notes_text_frame.text or "").strip()

        body = "\n".join(parts)
        blocks = [b for b in (title, body) if b.strip()]
        if notes:
            blocks.append("Notlar: " + notes)
        text = "\n".join(blocks)
        if text.strip():
            units.append(Unit("slide", f"Slayt {i}", title, text,
                              extra={"has_notes": bool(notes)}))
    return meta, units


# ------------------------------------------------------------------- xmind ---
# XMind files are ZIPs: newer (Zen/2020+) carry content.json, older (XMind 8)
# content.xml. Both are a tree of topics with titles + notes + labels.
def _strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s or "").strip()


def _xmind_dates(z: zipfile.ZipFile, p: Path) -> tuple[dt.datetime | None, dt.datetime | None, str | None]:
    """Best-effort creator/time from meta.json/meta.xml; else filesystem."""
    fs_created, fs_modified = _fs_dates(p)
    author = None
    try:
        if "meta.json" in z.namelist():
            m = json.loads(z.read("meta.json"))
            author = (m.get("creator", {}) or {}).get("name") if isinstance(m.get("creator"), dict) else None
    except Exception:
        pass
    return fs_created, fs_modified, author


def _flatten_json_topic(topic: dict, depth: int = 0) -> list[str]:
    lines = []
    title = (topic.get("title") or "").strip()
    if title:
        lines.append("  " * depth + title)
    n = topic.get("notes") or {}
    note = ""
    if isinstance(n, dict):
        note = ((n.get("plain") or {}).get("content")
                or _strip_html((n.get("realHTML") or n.get("html") or {}).get("content", "")
                               if isinstance(n.get("realHTML") or n.get("html"), dict) else ""))
    if note:
        lines.append("  " * depth + f"[Not: {note.strip()}]")
    for lab in topic.get("labels") or []:
        lines.append("  " * depth + f"[Etiket: {lab}]")
    ch = topic.get("children") or {}
    kids = []
    if isinstance(ch, dict):
        for key in ("attached", "detached", "callout", "summary"):
            kids += ch.get(key) or []
    for kid in kids:
        lines += _flatten_json_topic(kid, depth + 1)
    return lines


def _extract_xmind_json(content: bytes) -> tuple[str, list[Unit]]:
    data = json.loads(content)
    sheets = data if isinstance(data, list) else [data]
    units, doc_title = [], ""
    for si, sheet in enumerate(sheets, 1):
        root = sheet.get("rootTopic") or {}
        root_title = (root.get("title") or "").strip()
        sheet_title = (sheet.get("title") or root_title or f"Sayfa {si}").strip()
        if not doc_title:
            doc_title = root_title or sheet_title
        # each top-level branch becomes a unit; small maps -> one root unit
        ch = root.get("children") or {}
        branches = (ch.get("attached") or []) if isinstance(ch, dict) else []
        head = [x for x in _flatten_json_topic(root, 0) if x.strip()][:1]
        if branches:
            for b in branches:
                body = _flatten_json_topic(b, 0)
                text = "\n".join((head + body)).strip()
                if text:
                    units.append(Unit("mindmap", f"Harita: {sheet_title} / {(b.get('title') or '').strip()}",
                                      root_title, text))
        else:
            text = "\n".join(_flatten_json_topic(root, 0)).strip()
            if text:
                units.append(Unit("mindmap", f"Harita: {sheet_title}", root_title, text))
    return doc_title, units


def _localname(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _flatten_xml_topic(topic: ET.Element, depth: int = 0) -> list[str]:
    lines = []
    title = ""
    for ch in topic:
        if _localname(ch.tag) == "title":
            title = (ch.text or "").strip()
            break
    if title:
        lines.append("  " * depth + title)
    for ch in topic:
        if _localname(ch.tag) == "notes":
            for sub in ch:
                if _localname(sub.tag) in ("plain", "html"):
                    txt = "".join(sub.itertext()).strip()
                    if txt:
                        lines.append("  " * depth + f"[Not: {txt}]")
    for ch in topic:
        if _localname(ch.tag) == "children":
            for topics in ch:
                if _localname(topics.tag) == "topics":
                    for sub in topics:
                        if _localname(sub.tag) == "topic":
                            lines += _flatten_xml_topic(sub, depth + 1)
    return lines


def _extract_xmind_xml(content: bytes) -> tuple[str, list[Unit]]:
    root = ET.fromstring(content)
    units, doc_title = [], ""
    sheets = [e for e in root.iter() if _localname(e.tag) == "sheet"]
    for si, sheet in enumerate(sheets, 1):
        topic = next((e for e in sheet if _localname(e.tag) == "topic"), None)
        if topic is None:
            continue
        root_title = next(((c.text or "").strip() for c in topic
                           if _localname(c.tag) == "title"), "")
        if not doc_title:
            doc_title = root_title
        text = "\n".join(_flatten_xml_topic(topic, 0)).strip()
        if text:
            units.append(Unit("mindmap", f"Harita: {root_title or f'Sayfa {si}'}",
                              root_title, text))
    return doc_title, units


def extract_xmind(p: Path) -> tuple[DocMeta, list[Unit]]:
    with zipfile.ZipFile(str(p)) as z:
        names = set(z.namelist())
        if "content.json" in names:
            title, units = _extract_xmind_json(z.read("content.json"))
        elif "content.xml" in names:
            title, units = _extract_xmind_xml(z.read("content.xml"))
        else:
            title, units = "", []
        created, modified, author = _xmind_dates(z, p)
    meta = DocMeta(str(p), p.name, "xmind", created, modified, author, title or None)
    return meta, units


# ------------------------------------------------------------------ dispatch --
SUPPORTED = (".docx", ".pptx", ".xmind")


def extract(path: str | Path) -> tuple[DocMeta, list[Unit]]:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".docx":
        return extract_docx(p)
    if suffix == ".pptx":
        return extract_pptx(p)
    if suffix == ".xmind":
        return extract_xmind(p)
    raise ValueError(f"Desteklenmeyen dosya türü: {p.suffix} (yalnızca .docx / .pptx / .xmind)")


def iter_files(folder: str | Path):
    """Yield supported files under a folder, skipping Office lock/temp files."""
    root = Path(folder)
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() in SUPPORTED and not p.name.startswith("~$"):
            yield p


if __name__ == "__main__":
    import sys
    for f in iter_files(sys.argv[1] if len(sys.argv) > 1 else "."):
        meta, units = extract(f)
        print(f"\n=== {meta.name}  [{meta.kind}]  "
              f"created={meta.created:%Y-%m-%d} modified={meta.modified:%Y-%m-%d} "
              f"author={meta.author} title={meta.title}")
        for u in units:
            preview = u.text.replace("\n", " ⏎ ")[:90]
            print(f"   - {u.unit_id:<22} {preview}")
