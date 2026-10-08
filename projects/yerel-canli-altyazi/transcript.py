# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""The record of a session: written during, read afterwards.

The caption page deliberately forgets - it carries thirty seconds and no more.
This is the other half of that asymmetry: the complete meeting, on this machine
only, in a form notes.py can hand to a model for notes.

Plain text rather than JSON, on purpose. It is what a person reads to check the
record, and what the notes model reads to summarise it; a format that needs
parsing before either can happen would serve neither. read() exists to prove
the format survives a round trip - if we cannot parse what we write, the format
is wrong.
"""

import re
import time
from datetime import datetime

# [HH:MM:SS] (en) what was said
_ENTRY = re.compile(r"^\[(\d+):(\d\d):(\d\d)\]\s+\((\w+)\)\s+(.*)$")
_CONT = re.compile(r"^\s+\((\w+)\)\s+(.*)$")


def clock(seconds):
    """Seconds since the session began, as HH:MM:SS."""
    seconds = int(seconds)
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


class Transcript:
    """Append-only session record.

    Line-buffered, so a transcript survives the meeting even if the process is
    killed - which is exactly when you most want it.
    """

    def __init__(self, path, languages=None, source=None, started=None):
        self.path = path
        self.started = started or time.time()
        self.file = open(path, "w", encoding="utf-8", buffering=1)

        stamp = datetime.fromtimestamp(self.started).strftime("%Y-%m-%d %H:%M:%S")
        self.file.write("# Yazoğlum transcript\n")
        self.file.write(f"# started: {stamp}\n")
        if languages:
            self.file.write(f"# languages: {', '.join(languages)}\n")
        if source:
            self.file.write(f"# source: {source}\n")
        self.file.write("#\n# Times are elapsed from the start; add them to"
                        " 'started' for wall clock.\n\n")

    def add(self, said_lang, said, other_lang=None, translation=None, at=None):
        """Record one finished utterance. Provisional lines never come here.

        `at` is seconds into the audio. Falling back to the wall clock is only
        right for a live stream, where the two coincide.
        """
        elapsed = at if at is not None else time.time() - self.started
        self.file.write(f"[{clock(elapsed)}] ({said_lang or '??'}) {said}\n")
        if translation:
            self.file.write(f"           ({other_lang or '??'}) {translation}\n")
        self.file.write("\n")

    def close(self):
        if not self.file.closed:
            self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def read(path):
    """Parse a transcript back into (header, entries).

    entries are dicts: at (seconds), said_lang, said, other_lang, translation.
    """
    header, entries = {}, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            if ":" in line:
                key, _, value = line[1:].partition(":")
                key = key.strip()
                if key in ("started", "languages", "source"):
                    header[key] = value.strip()
            continue

        entry = _ENTRY.match(line)
        if entry:
            hours, minutes, seconds, lang, text = entry.groups()
            entries.append({
                "at": int(hours) * 3600 + int(minutes) * 60 + int(seconds),
                "said_lang": lang, "said": text,
                "other_lang": None, "translation": None,
            })
            continue

        # A continuation line belongs to the entry above it.
        more = _CONT.match(line)
        if more and entries:
            entries[-1]["other_lang"], entries[-1]["translation"] = more.groups()

    return header, entries


def as_prompt(entries, include_translation=False):
    """The transcript as the notes model should see it.

    Translations are left out by default: they are this tool's own output, not
    what anyone said, and feeding a model its own paraphrase alongside the
    original invites it to summarise the paraphrase.
    """
    lines = []
    for entry in entries:
        lines.append(f"[{clock(entry['at'])}] ({entry['said_lang']}) {entry['said']}")
        if include_translation and entry["translation"]:
            lines.append(f"           ({entry['other_lang']}) {entry['translation']}")
    return "\n".join(lines)
