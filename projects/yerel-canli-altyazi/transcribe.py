# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
import os
import sys

from huggingface_hub.utils import disable_progress_bars

disable_progress_bars()   # silence the "Fetching N files" bar on every run

MODEL = "mlx-community/whisper-large-v3-turbo"

# The GPU path's sizes, for --whisper. Full large-v3 has turbo's encoder and 32
# decoder layers instead of 4. Replayed on the demo meeting (8 Oct 2026) it got
# three Turkish words right that turbo missed ("müşteriye", "duyuracak", no
# stray "bu"), still heard "küçüğü" and German "des" for "bis", and on another
# recording of the same clips broke "düzeltirim". ~1.6 s per final line against
# turbo's ~1.2 s. Better, not right.
MLX_MODELS = {
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
}

# Two engines. "mlx" is Whisper large-v3-turbo on the Apple GPU - the big path.
# "faster-whisper" runs on the CPU of any machine, Mac or not - the small path.
# Measured on the scripted meeting cut into sentences exactly as live
# (5 Oct 2026, CPU, int8), word errors and time per second of audio:
#   small            6.8%   0.26x   keeps up live, with drafts and NLLB
#   medium           1.4%   0.80x   too slow live (lag grew to 186 s)
#   large-v3-turbo   0.0%   1.31x   too slow live; perfect after the meeting
# By language (same 18 sentences, macOS voices): small 20.8% on Turkish
# against 3.0% German and 3.4% English - the weakness is Turkish. Live Turkish
# captions from small were unusable; this engine is kept for the measurements
# and for re-transcribing a recording, not recommended. See DECISIONS.md.
ENGINE = "mlx"
SIZE = "small"

# The CPU path only listens for these. Whisper otherwise picks from 99
# languages on every utterance, and a wrong pick does not just mistranslate -
# it makes Whisper invent stock phrases in the language it guessed.
LANGUAGES = ("tr", "en", "de")

_fw = None


def configure(engine=None, size=None):
    global ENGINE, SIZE, MODEL
    if engine:
        ENGINE = engine
    if size:
        SIZE = size
        if ENGINE == "mlx":
            MODEL = MLX_MODELS[size]


def threads():
    """Half the cores: the translator shares the CPU with Whisper."""
    return max(1, (os.cpu_count() or 2) // 2)


def _faster_whisper(path, language=None, initial_prompt=None):
    global _fw
    if _fw is None:
        from faster_whisper import WhisperModel
        _fw = WhisperModel(SIZE, device="cpu", compute_type="int8", cpu_threads=threads())
    if language is None:
        _, _, probs = _fw.detect_language(path)
        language = max((p for p in probs if p[0] in LANGUAGES), key=lambda p: p[1])[0]
    segments, _ = _fw.transcribe(path, language=language, initial_prompt=initial_prompt,
                                 beam_size=1, vad_filter=False)
    segments = [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
    return {"language": language, "text": "".join(s["text"] for s in segments),
            "segments": segments}


def transcribe_file(path, language=None, initial_prompt=None):
    """Transcribe a file path or a float32 numpy array.

    language=None lets Whisper detect it from the first ~30s. Pass a code to
    pin it: detection costs an extra pass, and on a short utterance it can
    guess wrong and flip mid-stream.

    initial_prompt is text Whisper reads as "what came just before". On an
    utterance that starts mid-sentence it prevents a cold start, and keeps
    names spelled the same way across a cut. Keep it short - a long or
    repetitive prompt can send Whisper into a repetition loop.
    """
    if ENGINE == "faster-whisper":
        return _faster_whisper(path, language, initial_prompt)

    import mlx_whisper          # Apple Silicon only; imported only when used
    return mlx_whisper.transcribe(
        path,
        path_or_hf_repo=MODEL,
        language=language,
        initial_prompt=initial_prompt,
        verbose=None,
    )


if __name__ == "__main__":
    path = sys.argv[1]
    result = transcribe_file(path)
    print(f"language: {result['language']}")
    for seg in result["segments"]:
        print(f"[{seg['start']:6.2f} -> {seg['end']:6.2f}]  {seg['text'].strip()}")
