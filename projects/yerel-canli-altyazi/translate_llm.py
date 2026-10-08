# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""Translation through a local LLM served by Ollama.

translate.py (NLLB-200-distilled-600M) is a dedicated translation model: fast,
and wrong about terminology it was distilled past. "age reversal" came back as
"yas degisimi" (age *change*), "neuroscience" as "Noroloji" (the clinical
specialty, not the field), "computation" as "Bilgisayar" (the machine). A 27B
instruction model gets those right, at roughly 1.3s per line instead of 0.2s.

Same call signature as translate.to_turkish, so stream.py can hold either one
without knowing which.
"""

import json
import sys
import urllib.error
import urllib.request

# Default: this machine's own Ollama. Always available, no network dependency.
# qwen3.8 over qwen3.5 (measured 4 Oct 2026, 18 meeting lines x2): 3.5 turned
# "Mittwoch" into "Salı" and "Donnerstag" into the non-word "Dünürsü" EVERY run;
# 3.8 invented no words and its day slips were occasional. ~0.4s/line slower.
# Then the IQ4_XS quant of the same model (5 Oct, 18 lines x5, no checker):
# 0/90 day/number errors against 8/90 for the official Q4_K_M, which invented
# "Dün" (yesterday) 5 times and turned Mittwoch into "salı" twice. Re-run on
# 6 Oct: 2/54, the same "Dün" - better than Q4_K_M, not perfect; facts.py
# catches it. 15 GB, not 17. It is a community upload (batiai), not the Ollama library - say so to
# anyone told to pull it; the official Q4_K_M is the conservative choice.
HOST = "localhost"
MODEL = "batiai/qwen3.8-27b:iq4"

# Where to go when the configured host does not answer. A subtitle tool must
# not die mid-stream because another machine went to sleep.
FALLBACK_HOST = "localhost"
FALLBACK_MODEL = "batiai/qwen3.8-27b:iq4"

TIMEOUT = 120
KEEP_ALIVE = "30m"      # keep the weights resident; a cold load costs ~13s

# A meeting has a language PAIR, so the target changes per utterance: Turkish
# speech is shown with English beside it and vice versa. Turkish is no longer
# hardcoded anywhere below.
NAMES = {
    "tr": "Turkish", "en": "English", "de": "German", "fr": "French",
    "es": "Spanish", "it": "Italian", "pt": "Portuguese", "nl": "Dutch",
    "ru": "Russian", "ar": "Arabic", "el": "Greek", "pl": "Polish",
    "ja": "Japanese", "zh": "Chinese", "ko": "Korean", "sv": "Swedish",
    "uk": "Ukrainian", "fa": "Persian", "hi": "Hindi",
}


def _system(target):
    language = NAMES.get(target, target)
    return (f"You translate subtitles into {language}. Reply with ONLY the "
            f"{language} translation - no explanation, no quotes, no notes. "
            f"Keep technical terms accurate and natural.")

_warned = False


def configure(host=None, model=None):
    """Point at a different Ollama, e.g. configure("192.168.1.20", "qwen3.8:27b-q4_K_M")."""
    global HOST, MODEL
    if host:
        HOST = host
    if model:
        MODEL = model


def other(detected, pair):
    """The language to translate INTO, given what was just spoken.

    A pair like ("tr", "en") means: Turkish speech is shown with English, and
    anything else - including English - is shown with Turkish. So a stray third
    language still lands somewhere useful instead of failing.
    """
    first, second = pair
    return second if detected == first else first


def _clean(answer):
    """Strip the wrappers an instruction model sometimes adds around an answer.

    The system prompt asks for the bare translation, and usually gets it - but
    "only the translation" is a request, not a guarantee, and one stray
    'Turkish: "..."' on screen is worse than the cost of checking.
    """
    answer = (answer or "").strip()
    for lead in ("Turkish:", "Turkce:", "Türkçe:", "English:", "Translation:", "Çeviri:"):
        if answer.lower().startswith(lead.lower()):
            answer = answer[len(lead):].strip()
    if len(answer) > 1 and answer[0] == answer[-1] and answer[0] in "\"'“”":
        answer = answer[1:-1].strip()
    return answer


# A meeting glossary: plain lines like "yayın = Veröffentlichung (release, not
# broadcast)". Set with stream.py --glossary FILE. Translated alone, "Yayından
# sonra 24 saat geri dönüş seçeneğini açık tutalım" came back as a "refund option
# after the broadcast" in 3 runs of 3; with the glossary and the two lines
# before it, "Rollback-Option ... nach der Veröffentlichung" in 3 of 3.
GLOSSARY = ""


def _prompt(text, language, said, context):
    parts = []
    if GLOSSARY:
        parts.append(f"Meeting glossary:\n{GLOSSARY}")
    if context:
        # Originals only, never earlier translations: a translation error must
        # not become the context for the next one.
        parts.append("Earlier in this meeting (context only, do not translate):\n"
                     + "\n".join(context))
    parts.append(f"Translate this {said}subtitle line to {language}:\n\n{text}")
    return "\n\n".join(parts)


def _ask(host, model, text, target, source=None, context=None):
    language = NAMES.get(target, target)
    said = f"{NAMES[source]} " if source in NAMES else ""
    body = json.dumps({
        "model": model,
        "prompt": _prompt(text, language, said, context),
        "system": _system(target),
        "stream": False,
        "think": False,     # qwen3 reasons out loud otherwise; we want one line
        "keep_alive": KEEP_ALIVE,
        "options": {"temperature": 0.2, "num_predict": 200},
    }).encode()

    request = urllib.request.Request(
        f"http://{host}:11434/api/generate", body,
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return _clean(json.load(response).get("response", ""))


def translate(text, target="tr", source=None, context=None):
    """Translate into `target`, optionally told what language `text` is in.

    The source used to be left out on purpose: translate.py had to be TOLD the
    source language, and being told a wrong one made it hand the text back
    untranslated. Whisper now chooses only between tr/en/de and has not
    misdetected once; naming the source fixed a real error - unnamed, Aya read
    the German "Gut," as English "gut" and wrote "Sindir" (digest) - and did not
    change the 27B (2/54 fact errors either way, all caught by facts.py).

    `context` is a few earlier lines of the meeting, as "(tr) ..." strings, so
    the model can tell what an ambiguous word means here - see GLOSSARY.
    """
    global _warned

    text = (text or "").strip()
    if not text:
        return ""

    try:
        return _ask(HOST, MODEL, text, target, source, context)
    except (urllib.error.URLError, TimeoutError, OSError) as unreachable:
        if HOST == FALLBACK_HOST and MODEL == FALLBACK_MODEL:
            raise RuntimeError(
                f"ollama at {HOST}:11434 did not answer ({unreachable}). "
                f"Start it with:  ollama serve"
            ) from unreachable

        if not _warned:
            print(f"[translate] {HOST} unreachable ({unreachable}); falling back "
                  f"to {FALLBACK_HOST} / {FALLBACK_MODEL}", file=sys.stderr)
            _warned = True
        return _ask(FALLBACK_HOST, FALLBACK_MODEL, text, target, source, context)


def to_turkish(text, src=None):
    """Back-compat shim: same signature as translate.py's function."""
    return translate(text, "tr")


if __name__ == "__main__":
    import time

    if len(sys.argv) > 1:
        configure(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

    print(f"{HOST} / {MODEL}\n")
    for line in ("age reversal",
                 "The Yamanaka factors can drive age reversal in cells.",
                 "Those cells are different because the genes in the DNA are turned on and off."):
        start = time.time()
        print(f"  EN {line}")
        print(f"  TR {translate(line, 'tr')}")
        print(f"     [{time.time() - start:.2f}s]\n")
