#!/usr/bin/env python3
"""Turkish relative-time parsing for date-filtered search.

Turns phrases like "geçen hafta", "bu ay", "dün", "geçen yıl", "son 3 gün",
"ağustos" into a (start_date, end_date) range, and returns the query with the
time phrase removed so the rest can drive semantic/keyword search.

Week starts Monday (Turkish convention). Reference date is injectable for tests.
"""
from __future__ import annotations

import calendar
import datetime as dt
import re

MONTHS = {
    "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5,
    "mayis": 5, "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8,
    "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11, "kasim": 11,
    "aralık": 12, "aralik": 12,
}


def _week_bounds(d: dt.date) -> tuple[dt.date, dt.date]:
    monday = d - dt.timedelta(days=d.weekday())
    return monday, monday + dt.timedelta(days=6)


def _month_bounds(year: int, month: int) -> tuple[dt.date, dt.date]:
    last = calendar.monthrange(year, month)[1]
    return dt.date(year, month, 1), dt.date(year, month, last)


def parse(query: str, today: dt.date | None = None) -> tuple[tuple[dt.date, dt.date] | None, str]:
    """Return ((start, end) | None, query_without_time_phrase)."""
    today = today or dt.date.today()
    q = query
    rng: tuple[dt.date, dt.date] | None = None

    def strip(pattern):
        nonlocal q
        q = re.sub(pattern, " ", q, flags=re.IGNORECASE).strip()

    low = query.lower()

    # --- explicit day-count windows: "son 3 gün", "son 2 hafta" ---
    m = re.search(r"son\s+(\d+)\s+gün", low)
    if m:
        n = int(m.group(1))
        rng = (today - dt.timedelta(days=n), today)
        strip(r"son\s+\d+\s+gün\w*")
        return rng, q
    m = re.search(r"son\s+(\d+)\s+hafta", low)
    if m:
        n = int(m.group(1))
        rng = (today - dt.timedelta(weeks=n), today)
        strip(r"son\s+\d+\s+hafta\w*")
        return rng, q

    # --- day-level ---
    if "bugün" in low:
        rng = (today, today); strip(r"bugün")
    elif "dünkü" in low or re.search(r"\bdün\b", low):
        y = today - dt.timedelta(days=1); rng = (y, y); strip(r"dünkü|dün")
    elif "evvelsi gün" in low or "önceki gün" in low:
        y = today - dt.timedelta(days=2); rng = (y, y); strip(r"evvelsi gün|önceki gün")

    # --- week ---
    elif "bu hafta" in low or "bu haftaki" in low:
        rng = _week_bounds(today); strip(r"bu haftaki|bu hafta")
    elif "geçen hafta" in low or "geçen haftaki" in low or "gecen hafta" in low:
        rng = _week_bounds(today - dt.timedelta(days=7)); strip(r"geçen haftaki|geçen hafta|gecen haftaki|gecen hafta")

    # --- month ---
    elif "bu ay" in low or "bu ayki" in low:
        rng = _month_bounds(today.year, today.month); strip(r"bu ayki|bu ay")
    elif "geçen ay" in low or "gecen ay" in low or "geçen ayki" in low:
        first = today.replace(day=1) - dt.timedelta(days=1)
        rng = _month_bounds(first.year, first.month); strip(r"geçen ayki|geçen ay|gecen ayki|gecen ay")

    # --- year ---
    elif "bu yıl" in low or "bu sene" in low:
        rng = (dt.date(today.year, 1, 1), dt.date(today.year, 12, 31)); strip(r"bu yıl|bu sene")
    elif "geçen yıl" in low or "geçen sene" in low or "gecen yıl" in low:
        y = today.year - 1
        rng = (dt.date(y, 1, 1), dt.date(y, 12, 31)); strip(r"geçen yıl|geçen sene|gecen yıl")

    # --- bare month name ("ağustos raporu") -> that month, this year (or last if future) ---
    if rng is None:
        for name, mon in MONTHS.items():
            if re.search(rf"\b{name}\b", low):
                year = today.year if mon <= today.month else today.year - 1
                rng = _month_bounds(year, mon); strip(rf"\b{name}\b")
                break

    return rng, re.sub(r"\s+", " ", q).strip()


if __name__ == "__main__":
    ref = dt.date(2026, 8, 22)
    for qs in ["geçen haftaki toplantı notları", "bu haftaki toplantı", "dün gelen dilekçe",
               "geçen ay proje raporu", "ağustos bütçe", "son 3 gün fatura", "geçen yıl sözleşme"]:
        rng, rest = parse(qs, today=ref)
        s = f"{rng[0]}..{rng[1]}" if rng else "—"
        print(f"  {qs:<38} -> [{s}]  kalan: {rest!r}")
