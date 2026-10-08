# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""Meeting notes from a transcript, on this machine.

Zoom, Teams and Meet all summarise meetings now, and all of them do it by
sending the meeting to a company. This does the same job with the same model
already resident for translation - nothing leaves the machine.

Usage:  notes.py TRANSCRIPT [--out FILE] [--ollama HOST] [--model NAME] [--glossary FILE] [--cpu]
"""

import json
import sys
import urllib.error
import urllib.request

import facts
import transcript
import translate_llm

TIMEOUT = 900       # a long meeting is a long prompt; the model may think a while

SYSTEM = """You write meeting notes in Turkish from a transcript.

The transcript is machine-transcribed speech, so:

- It contains SPOKEN CORRECTIONS. A speaker who says "sorry, correction, I said
  Wednesday, not tomorrow" is fixing something said earlier. Always use the
  corrected value, and never report the original mistake as if it stood.
- Transcription errors happen. Where a line is garbled, rely on the surrounding
  lines; do not invent detail to smooth it over.
- There are no speaker names. Write what was decided and what was undertaken,
  not who said it, unless a name is spoken aloud in the transcript itself.
- Lines may be in more than one language. A line not spoken in Turkish is
  followed by its Turkish translation, marked "(tr)". Take your Turkish WORDING
  from those translations and from the Turkish lines. But take every FACT -
  days, times, dates, numbers, names - from the ORIGINAL line: a translation
  can be wrong, the original is what was said.
- Never build a word out of a foreign stem with a Turkish ending. If a term has
  no Turkish word in the transcript, use a plain everyday Turkish word.
- No glosses in brackets: write "geri dönüş seçeneği", never
  "geri dönüş (rollback) seçeneği". One word for one thing, in Turkish.

Write ONLY the notes, in this shape, in Turkish. Leave a heading out entirely if
there is nothing real to put under it - do not pad:

## Kararlar
## Yapılacaklar
## Açık Sorular

Be brief and concrete. Every line must be traceable to something actually said."""


def as_prompt(entries):
    """What was said, plus the Turkish translation of every non-Turkish line.

    transcript.as_prompt() leaves translations out so the model summarises what
    people said, not a paraphrase. But then a German line reaches the model in
    German, and it translates while it summarises - which is where it coined
    "Projektleme" from "Projektleitung", although the live translation already
    read "proje yonetimi". So the Turkish is given as the wording; the original
    stays first, as the record.
    """
    lines = []
    for entry in entries:
        said, translation = entry["said"], entry["translation"]
        lines.append(f"[{transcript.clock(entry['at'])}] ({entry['said_lang']}) {said}")
        if entry["said_lang"] == "tr" or entry["other_lang"] != "tr" or not translation:
            continue
        # Telling the model to take facts from the original was not enough: it
        # copied "salı" from a wrong translation in 3 runs of 3. So a translation
        # whose days or numbers disagree with what was said never reaches it -
        # repaired if only the weekday was swapped, otherwise left out.
        if not facts.same(said, translation):
            translation = facts.repair(said, translation, "tr")
        if translation:
            lines.append(f"           (tr) {translation}")
    return "\n".join(lines)


def fill_gaps(entries):
    """Re-translate the lines whose live translation was withheld or wrong.

    Live, a translation that changes a day or a time is not shown (facts.py),
    so on the CPU path "bis Mittwoch, 16 Uhr" reached the transcript with no
    Turkish at all - NLLB had made it "saat dört". The notes model then
    skipped the line: the release-notes deadline was missing in 3 runs of 3.
    After the meeting there is time, so the notes model translates those lines
    itself, under the same check. Whatever still fails stays original-only.
    """
    # The same guard as live - a swapped weekday is repaired from the original -
    # and two tries: Aya wrote "Salı" for "Mittwoch" once, then right twice.
    checked = facts.checked(lambda text, src, target: translate_llm.translate(text, target))
    filled = []
    for entry in entries:
        said, translation = entry["said"], entry["translation"]
        # A withheld line is logged with no target language at all, so the
        # test is "not Turkish and no good Turkish", not other_lang == "tr".
        if (entry["said_lang"] != "tr" and entry["other_lang"] in ("tr", None)
                and not (translation and facts.same(said, translation))):
            try:
                again = (checked(said, entry["said_lang"], "tr")
                         or checked(said, entry["said_lang"], "tr"))
                if again:
                    entry = dict(entry, translation=again, other_lang="tr")
            except RuntimeError:
                pass
        filled.append(entry)
    return filled


def write(entries, host=None, model=None, timeout=TIMEOUT):
    """Ask the local model for notes over these transcript entries."""
    if not entries:
        return "(transcript is empty)"

    translate_llm.configure(host, model)
    entries = fill_gaps(entries)
    body = json.dumps({
        "model": translate_llm.MODEL,
        "system": SYSTEM,
        "prompt": ("Here is the transcript. Write the meeting notes in Turkish.\n\n"
                   + as_prompt(entries)),
        "stream": False,
        "think": False,
        "keep_alive": translate_llm.KEEP_ALIVE,
        # Low but not zero: notes need to phrase things, not just copy them.
        # 0.3 was too loose for Aya 8B: in 1 run of 5 it turned the open
        # question ("tell the customer?") into a decision nobody made. At 0.1,
        # 5 of 5 were correct and complete.
        "options": {"temperature": 0.1, "num_predict": 1500},
    }).encode()

    request = urllib.request.Request(
        f"http://{translate_llm.HOST}:11434/api/generate", body,
        {"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response).get("response", "").strip()
    except (urllib.error.URLError, TimeoutError, OSError) as unreachable:
        raise RuntimeError(
            f"ollama at {translate_llm.HOST}:11434 did not answer ({unreachable}). "
            f"Start it with:  ollama serve"
        ) from unreachable


def main(argv):
    path = None
    out = host = model = None
    rest = list(argv)
    for flag in ("--out", "--ollama", "--model", "--glossary"):
        if flag in rest:
            at = rest.index(flag)
            value = rest[at + 1]
            rest = rest[:at] + rest[at + 2:]
            if flag == "--out":
                out = value
            elif flag == "--ollama":
                host = value
            elif flag == "--glossary":
                translate_llm.GLOSSARY = open(value, encoding="utf-8").read().strip()
            else:
                model = value
    # The small path writes notes with Aya Expanse 8B: on CPU it took 22-67 s
    # and got every day and time right in both runs on the scripted meeting;
    # qwen2.5 7B moved a deadline to the wrong day. Speed does not matter here -
    # the meeting is over - so this is where the bigger model belongs.
    if "--cpu" in rest:
        rest.remove("--cpu")
        model = model or "aya-expanse:8b"
    if not rest:
        print(__doc__.strip())
        return 1
    path = rest[0]

    header, entries = transcript.read(path)
    print(f"{path}: {len(entries)} utterances"
          + (f", started {header['started']}" if "started" in header else ""),
          file=sys.stderr)

    notes = write(entries, host, model)

    # A day or number nobody said is a false record. Checked in code, not
    # trusted to the prompt; flagged here so it is fixed before anyone sees it.
    words, numbers = facts.unsaid(notes, [entry["said"] for entry in entries])
    if words or numbers:
        print(f"\n⚠ CHECK BEFORE SHARING - not said in the meeting: "
              f"{', '.join(words + [str(n) for n in numbers])}\n",
              file=sys.stderr)

    if out:
        open(out, "w", encoding="utf-8").write(notes + "\n")
        print(f"notes written to {out}", file=sys.stderr)
    else:
        print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
