# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
import re

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


MODEL = "facebook/nllb-200-distilled-600M"
# The Apple GPU when there is one; the CPU otherwise, and always on the --cpu
# path, where NLLB measured 0.24 s a line - fast enough to cost almost no lag.
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# Whisper reports ISO 639-1 ("pt"). NLLB wants language + script ("por_Latn"),
# because it separates e.g. Chinese written simplified from traditional.
# Grouped by script; every code verified against the NLLB tokenizer vocabulary.
LANG = {
    # Latin
    "en": "eng_Latn",
    "de": "deu_Latn",
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "pt": "por_Latn",
    "it": "ita_Latn",
    "nl": "nld_Latn",
    "pl": "pol_Latn",
    "sv": "swe_Latn",
    "tr": "tur_Latn",
    # other scripts
    "el": "ell_Grek",
    "ru": "rus_Cyrl",
    "uk": "ukr_Cyrl",
    "ar": "arb_Arab",
    "fa": "pes_Arab",
    "hi": "hin_Deva",
    "ja": "jpn_Jpan",
    "zh": "zho_Hans",   # simplified; zho_Hant for traditional
    "ko": "kor_Hang",
}


# NLLB was trained on SENTENCE pairs. Hand it two sentences and it may merge
# them or drop one outright ("Olá, bom dia. Como está você?" -> "Merhaba, iyi
# günler."). So we split first and translate one sentence at a time.
_SPLIT = re.compile(r"(?<=[.!?\u2026])\s+")

# A period after one of these is an abbreviation, not a sentence end. Without
# this, "your host, Dr. Ginger Campbell." breaks into "your host, Dr." plus
# "Ginger Campbell." - two fragments that translate to nonsense.
_ABBR = {"dr", "mr", "mrs", "ms", "st", "prof", "vs", "etc", "no", "jr", "sr"}


def sentences(text):
    """Split text into sentences, keeping abbreviations intact.

    Whisper punctuates its output, so splitting on .!?... is usually enough.
    Text with no punctuation at all comes back as a single piece.
    """
    out, buf = [], ""
    for piece in _SPLIT.split(text.strip()):
        buf = f"{buf} {piece}".strip() if buf else piece
        words = buf.rstrip(".!?\u2026").split()
        if words and words[-1].lower() in _ABBR:
            continue          # false split - glue it back and keep going
        out.append(buf)
        buf = ""
    if buf:
        out.append(buf)
    return [p for p in out if p]


_tok = None
_model = None


def load():
    global _tok, _model
    if _model is None:
        _tok = AutoTokenizer.from_pretrained(MODEL)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL).to(DEVICE)
        _model.eval()
        _model.generation_config.max_length = None
    return _tok, _model


def translate(text, src, target="tr"):
    """Translate `text` from `src` into `target`, both ISO 639-1.

    NLLB needs to be TOLD both languages - unlike the LLM, which works the
    source out itself. That is the trade: this is ~6x faster and knows less.
    """
    # Look up BEFORE load(): an unknown language should fail in milliseconds,
    # not after pulling 2.4 GB of model weights onto the GPU.
    code = LANG.get(src)
    into = LANG.get(target)
    if code is None or into is None:
        unknown = src if code is None else target
        raise ValueError(
            f"no NLLB code for Whisper language {unknown!r} - "
            f"add it to LANG in translate.py (known: {', '.join(sorted(LANG))})"
        )

    # One sentence per row, so the model never has to summarise across a
    # sentence boundary - that is where content used to disappear.
    parts = sentences(text)
    if not parts:
        return ""

    tok, model = load()
    tok.src_lang = code

    # padding=True pads the rows to equal length so they travel as one batch:
    # a single GPU round-trip for the whole utterance instead of one per
    # sentence. attention_mask (built by the tokenizer) tells the model which
    # positions are padding, so the extra tokens change nothing.
    inputs = tok(parts, return_tensors="pt", padding=True).to(DEVICE)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=tok.convert_tokens_to_ids(into),
            max_new_tokens=256,
        )
    # NLLB was trained partly on subtitles, where a leading "-" marks a change
    # of speaker. It emits that dash on short lines ("It's fine." -> "- Tamamdır.")
    # even when there is no dialogue. Strip it per sentence, not per utterance.
    pieces = [p.lstrip("-\u2013\u2014 ").strip()
              for p in tok.batch_decode(outputs, skip_special_tokens=True)]
    return " ".join(p for p in pieces if p)


def to_turkish(text, src):
    """Back-compat shim for callers that predate the language pair."""
    return translate(text, src, "tr")


if __name__ == "__main__":
    print(translate("Hello, this is my first transcription.", "en", "tr"))
    print(translate("Raporu Çarşamba günü teslim edeceğim.", "tr", "en"))