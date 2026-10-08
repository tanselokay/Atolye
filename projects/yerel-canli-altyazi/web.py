# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""The caption page participants open, served from this machine.

Two jobs, and the second is the one that shapes the design:
  1. show what is being said, in both session languages;
  2. let a speaker SEE what the system understood and object on the spot
     ("I said Wednesday, not tomorrow").

So the original and the translation carry equal weight - this is a verification
surface, not decoration.

What it deliberately is NOT is a transcript. The server only ever sends the last
RETAIN_S seconds, and each push REPLACES what the browser holds rather than
appending, so a participant's page cannot accumulate the meeting. That is a
distribution choice, not a security control - anyone can screen-record - but it
means nobody is handed a record they can scroll from end to beginning.
"""

import json
import queue
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import display

PORT = 8770        # 8765 is a common default for other local tools
CHROMA = "#00FF00"      # exactly the green Wirecast keys on; do not "improve" it
# Re-broadcast interval: lines age out during silence, and a rewrite held back
# by MIN_DWELL reaches the page on the next tick - at 2 s that added up to two
# seconds to a final line that was already there.
TICK_S = 0.5

PAGE = r"""<!doctype html>
<html lang="tr">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Yazoğlum</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { height:100%; background:#101014; color:#fff;
               font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; }
  body.chroma { background:__CHROMA__; }

  /* Sizes are in px scaled by --scale, NOT vh. vh looked right in a full-screen
     Wirecast canvas and shrank to nothing the moment the window was resized
     smaller - which is exactly what happens while setting a shot up. ?size=N
     scales everything at once. */
  :root { --scale: 1; }

  #stage { height:100%; display:flex; flex-direction:column; justify-content:flex-end;
           padding:calc(24px * var(--scale)) calc(40px * var(--scale))
                   calc(40px * var(--scale));
           overflow-y:auto; scroll-behavior:smooth; }
  #stage::-webkit-scrollbar { width:0; }        /* scrolling works, bar stays out of shot */

  .entry { margin-top:calc(14px * var(--scale)); }
  .said, .other { line-height:1.25; }

  /* Who said it. The pipeline knows the LANGUAGE, not the person, so the bar
     is coloured by spoken language - which is the speaker whenever each person
     speaks their own language. A thin rule between turns does the rest. */
  .entry { border-left:calc(5px * var(--scale)) solid var(--who, #5a6372);
           padding-left:calc(14px * var(--scale)); }
  .entry + .entry { border-top:1px solid rgba(255,255,255,.12);
                    padding-top:calc(12px * var(--scale)); }
  .entry[data-lang="tr"] { --who:#e8a33d; }
  .entry[data-lang="de"] { --who:#4aa8e8; }
  body.chroma .entry { border-left:0; border-top:0; padding-left:0; }

  /* Both white: a speaker checks the ORIGINAL against what they said, so it is
     not secondary text. Size and weight separate them, not colour - which also
     keys more cleanly than a grey that sits nearer the green. */
  .said  { font-size:calc(26px * var(--scale)); font-weight:600; color:#fff; opacity:.82; }
  .other { font-size:calc(34px * var(--scale)); font-weight:700; color:#fff; }

  body.chroma .said,
  body.chroma .other { opacity:1; -webkit-text-stroke:calc(3px * var(--scale)) #000;
                       paint-order:stroke fill; }

  /* Still being spoken: visibly unsettled, so nobody reads it as the record.
     The translation is dimmed too - a provisional line is NLLB's rough pass,
     and the LLM will replace it within a couple of seconds. */
  .provisional .said,
  .provisional .other { font-style:italic; opacity:.6; }
  .provisional .other::after { content:" …"; }

  .tag { display:inline-block; font-size:calc(13px * var(--scale)); font-weight:700;
         letter-spacing:.08em; text-transform:uppercase; color:#7c8797;
         margin-right:.6em; vertical-align:.15em; }
  body.chroma .tag { display:none; }            /* no chrome in the keyed output */

  #live { position:fixed; left:50%; transform:translateX(-50%); bottom:2.4vh;
          background:#e33; color:#fff; border:0; border-radius:2em;
          padding:.7em 1.4em; font-size:1.9vh; font-weight:700; cursor:pointer;
          display:none; box-shadow:0 .4vh 1.6vh rgba(0,0,0,.45); }
  #live.show { display:block; }
</style>

<div id="stage"></div>
<button id="live">↓ Canlı</button>

<script>
  const params  = new URLSearchParams(location.search);
  if (params.get("key") === "green") document.body.classList.add("chroma");
  // ?size=1.6 makes everything bigger; the page no longer resizes with the window.
  const scale = parseFloat(params.get("size") || "1");
  if (scale > 0) document.documentElement.style.setProperty("--scale", scale);

  const stage = document.getElementById("stage");
  const live  = document.getElementById("live");

  // Scrolling IS the pause. Away from the bottom -> frozen; back at the bottom
  // -> live again. Every chat app works this way, so nobody needs telling.
  let following = true;
  const atBottom = () => stage.scrollHeight - stage.scrollTop - stage.clientHeight < 24;

  stage.addEventListener("scroll", () => {
    following = atBottom();
    live.classList.toggle("show", !following);
  });

  function goLive() {
    following = true;
    live.classList.remove("show");
    if (pending) { render(pending); pending = null; }
    stage.scrollTop = stage.scrollHeight;
  }
  live.addEventListener("click", goLive);
  addEventListener("keydown", (e) => {
    if (e.code === "Space") { e.preventDefault(); following ? stage.scrollBy(0,-120) : goLive(); }
  });

  let pending = null;

  function render(rows) {
    stage.replaceChildren();
    for (const row of rows) {
      const entry = document.createElement("div");
      entry.className = "entry" + (row.final === false ? " provisional" : "");
      if (row.said_lang) entry.dataset.lang = row.said_lang;
      if (row.source) {
        const said = document.createElement("div");
        said.className = "said";
        if (row.said_lang) {
          const tag = document.createElement("span");
          tag.className = "tag"; tag.textContent = row.said_lang;
          said.appendChild(tag);
        }
        said.appendChild(document.createTextNode(row.source));
        entry.appendChild(said);
      }
      if (!row.text) { stage.appendChild(entry); continue; }   // provisional: original only
      const other = document.createElement("div");
      other.className = "other";
      if (row.other_lang) {
        const tag = document.createElement("span");
        tag.className = "tag"; tag.textContent = row.other_lang;
        other.appendChild(tag);
      }
      other.appendChild(document.createTextNode(row.text));
      entry.appendChild(other);
      stage.appendChild(entry);
    }
    if (following) stage.scrollTop = stage.scrollHeight;
  }

  // EventSource reconnects by itself, which matters: this page stays open on a
  // participant's screen across restarts of the pipeline.
  const events = new EventSource("/events");
  events.onmessage = (e) => {
    const rows = JSON.parse(e.data);
    // Frozen: hold the snapshot the reader is looking at. On resume we take the
    // CURRENT window whole - the browser never merges, so it never accumulates.
    if (following) render(rows); else pending = rows;
  };
</script>
</html>
"""


def lan_address():
    """This machine's address on the LAN - the one participants can actually open.

    No packet is sent: connecting a UDP socket only makes the OS choose the
    interface it would route through, which is exactly the address we want.
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))     # TEST-NET-1, guaranteed unroutable
        return probe.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


class CaptionServer:
    """Serves the page and pushes the current caption window to every browser."""

    def __init__(self, port=PORT, lines=1, retain_s=display.RETAIN_S):
        # lines=1 means ONE utterance on screen, which is two rows: what was
        # said and its translation. That is the shape burned-in subtitles have
        # always had, and it is what fits in a small Zoom tile.
        self.port = port
        # One display contract for every surface: the terminal renderer and this
        # page hold the same Captions class, so dwell and replace-by-key cannot
        # drift apart between them.
        self.board = display.Captions(lines=lines, min_dwell=display.MIN_DWELL,
                                      retain_s=retain_s)
        self.meta = {}                 # key -> (said_lang, other_lang)
        self.clients = []
        self.lock = threading.Lock()
        self.httpd = None

    # ---- what the pipeline calls -------------------------------------------

    def show(self, key, text, source=None, said_lang=None, other_lang=None, final=True):
        with self.lock:
            self.board.show(key, text, source=source)
            self.meta[key] = (said_lang, other_lang, final)
        self.broadcast()

    def _payload(self):
        rows = self.board.payload()
        for row in rows:
            said_lang, other_lang, final = self.meta.get(row["key"], (None, None, True))
            row["said_lang"], row["other_lang"], row["final"] = said_lang, other_lang, final
        live = {row["key"] for row in rows}
        self.meta = {k: v for k, v in self.meta.items() if k in live}
        return json.dumps(rows, ensure_ascii=False)

    def broadcast(self):
        with self.lock:
            payload = self._payload()
            listeners = list(self.clients)
        for client in listeners:
            client.put(payload)

    # ---- serving ------------------------------------------------------------

    def start(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass                   # the default logger writes over the captions

            def do_GET(self):
                if self.path.startswith("/events"):
                    return self._events()
                body = PAGE.replace("__CHROMA__", CHROMA).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _events(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()

                mine = queue.Queue()
                with server.lock:
                    server.clients.append(mine)
                    mine.put(server._payload())   # late joiners are not blank
                try:
                    while True:
                        self.wfile.write(f"data: {mine.get()}\n\n".encode("utf-8"))
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, ValueError):
                    pass
                finally:
                    with server.lock:
                        if mine in server.clients:
                            server.clients.remove(mine)

        self.httpd = ThreadingHTTPServer(("0.0.0.0", self.port), Handler)
        self.httpd.daemon_threads = True
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

        # Without a tick, a line that stops being pushed would sit on screen for
        # ever: retain_s only prunes when the window is recomputed.
        def tick():
            while True:
                time.sleep(TICK_S)
                self.broadcast()
        threading.Thread(target=tick, daemon=True).start()
        return self


if __name__ == "__main__":
    import itertools
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    server = CaptionServer(port=port).start()
    print(f"http://127.0.0.1:{server.port}              participants")
    print(f"http://127.0.0.1:{server.port}/?key=green   Wirecast source")
    print("Ctrl-C to stop\n")

    demo = [
        ("en", "tr", "I will deliver it on Wednesday.", "Çarşamba günü teslim edeceğim."),
        ("tr", "en", "Toplantı notlarını ben hazırlarım.", "I will prepare the meeting notes."),
        ("en", "tr", "Can we push the review to next week?",
         "İncelemeyi haftaya erteleyebilir miyiz?"),
    ]
    try:
        for n in itertools.count(1):
            said_lang, other_lang, source, text = demo[(n - 1) % len(demo)]
            server.show(n, text, source=source, said_lang=said_lang, other_lang=other_lang)
            print(f"  {n}. [{said_lang}] {source}\n     [{other_lang}] {text}")
            time.sleep(5)
    except KeyboardInterrupt:
        sys.exit(0)
