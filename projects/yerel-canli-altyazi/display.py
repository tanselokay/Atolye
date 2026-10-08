# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""What reaches the screen, and for how long.

The pipeline decides WHAT was said; this decides what is VISIBLE. Keeping them
apart is what lets the same subtitles go to a terminal now and to a chroma-key
browser page later without the pipeline noticing.
"""

import shutil
import sys
import textwrap
import time
from collections import deque

LINES = 2            # subtitle entries visible at once
MIN_DWELL = 1.5      # seconds a line is protected from being rewritten
RETAIN_S = 30        # web only: how far back a viewer can scroll, in seconds


class Captions:
    """A rolling window over the last few subtitles.

    show(key, text) adds a line, or REPLACES the line with the same key. That
    replacement is the whole reason this class exists: a provisional
    translation can appear early and be rewritten in place once the complete
    utterance is known - which is how the grey draft lines become final ones
    without the renderer knowing the difference.

    MIN_DWELL protects a reader from text that changes before it can be read.
    A rewrite arriving too soon is held and applied on the next update, so a
    line never flickers through three versions in half a second.
    """

    def __init__(self, lines=LINES, min_dwell=MIN_DWELL, retain_s=None):
        self.lines = lines
        self.min_dwell = min_dwell
        # retain_s bounds the window by TIME as well as count. The web page uses
        # it so a participant can scroll back ~30s to check a line and no
        # further: what was never sent cannot become a transcript.
        self.retain_s = retain_s
        self.rows = deque()      # (key, text, first_shown, source)
        self.held = {}           # key -> text waiting out MIN_DWELL

    def show(self, key, text, now=None, source=None):
        now = time.monotonic() if now is None else now
        self._flush(now)

        for i, (existing, current, shown_at, was) in enumerate(self.rows):
            if existing == key:
                if text != current and now - shown_at < self.min_dwell:
                    # Too soon; rewrite later - the original WITH the
                    # translation. Holding the translation alone kept the
                    # draft's unfinished original on the page for good:
                    # "Testler planlanandan iki gün daha uzun." next to the
                    # final translation of the whole sentence.
                    self.held[key] = (text, source or was)
                else:
                    # Keep the original timestamp: a rewrite is the same line,
                    # so it must not win itself a fresh dwell period.
                    self.rows[i] = (key, text, shown_at, source or was)
                    self.held.pop(key, None)
                return

        self.rows.append((key, text, now, source))
        while len(self.rows) > self.lines:
            dropped = self.rows.popleft()[0]
            self.held.pop(dropped, None)

    def _flush(self, now):
        """Apply rewrites whose dwell has passed, and drop rows past retain_s."""
        for i, (key, current, shown_at, source) in enumerate(self.rows):
            if key in self.held and now - shown_at >= self.min_dwell:
                text, held_source = self.held.pop(key)
                self.rows[i] = (key, text, shown_at, held_source)

        while self.retain_s and self.rows and now - self.rows[0][2] > self.retain_s:
            self.held.pop(self.rows.popleft()[0], None)

    def visible(self, now=None):
        """The lines that should be on screen, oldest first."""
        self._flush(time.monotonic() if now is None else now)
        return [text for _, text, _, _ in self.rows]

    def rows_visible(self, now=None):
        """(text, source) for every visible line - source may be None."""
        self._flush(time.monotonic() if now is None else now)
        return [(text, source) for _, text, _, source in self.rows]

    def payload(self, now=None):
        """Visible rows as dicts, for the browser."""
        self._flush(time.monotonic() if now is None else now)
        return [{"key": key, "text": text, "source": source}
                for key, text, _, source in self.rows]


DIM, RESET = "\x1b[2m", "\x1b[0m"


class Terminal:
    """Draw the caption area in place, so subtitles replace instead of scrolling.

    Each redraw walks the cursor back over the rows it printed last time and
    overwrites them. That is why it counts PHYSICAL rows, not subtitles: a long
    line wraps to several rows and the cursor has to climb all of them.
    """

    def __init__(self, captions, show_source=True, width=None, out=sys.stdout):
        self.captions = captions
        self.show_source = show_source
        self.width = width
        self.out = out
        self.drawn = 0

    def _width(self):
        return self.width or max(28, shutil.get_terminal_size((80, 24)).columns - 2)

    def _compose(self):
        width, rows = self._width(), []
        for text, source in self.captions.rows_visible():
            if self.show_source and source:
                rows += [DIM + line + RESET
                         for line in textwrap.wrap(source, width) or [""]]
            rows += textwrap.wrap(text, width) or [""]
        return rows

    def draw(self):
        rows = self._compose()

        if self.drawn:
            self.out.write(f"\x1b[{self.drawn}A")     # climb to the top of the area

        for row in rows:
            self.out.write("\x1b[2K" + row + "\n")   # clear the row, then write it

        # If this frame is shorter than the last, blank the leftover rows and
        # step back up over them, so the cursor ends exactly below the text and
        # the area does not creep downward.
        extra = max(0, self.drawn - len(rows))
        for _ in range(extra):
            self.out.write("\x1b[2K\n")
        if extra:
            self.out.write(f"\x1b[{extra}A")

        self.drawn = len(rows)
        self.out.flush()
