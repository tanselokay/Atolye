# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
import subprocess
import sys
import threading

from collections import deque

from typing import NamedTuple

import numpy as np
from silero_vad import load_silero_vad, VADIterator

import transcribe
from translate_llm import other

SR = 16000
CHUNK = 512
MIN_SILENCE_MS = 600

# A speaker who never pauses would otherwise hold the whole stream hostage:
# nothing reaches the screen until they stop talking. Cut anyway after this
# long, so a subtitle always appears.
#
# This constant IS the latency: measured on an 89s podcast, lag tracks it
# almost 1:1 (7.0s cap -> 7.4s median lag; 4.0s -> 4.3s; 2.0s -> 2.3s) because
# compute is only ~0.4s per utterance. Lower it for responsiveness, raise it
# for fewer mid-sentence cuts. At 4.0s the pipeline still runs 10x realtime.
MAX_UTTERANCE_S = 6.0
MAX_SAMPLES = int(MAX_UTTERANCE_S * SR)

# Replay this much audio at the start of the next utterance after a forced
# cut. A word straddling the cut is otherwise sliced mid-syllable and comes
# back as nonsense; with the overlap it is heard whole at least once. The
# cost is that a short word may be transcribed twice.
OVERLAP_S = 0.3
OVERLAP_SAMPLES = int(OVERLAP_S * SR)

# Keep this much audio from BEFORE the VAD fired. It fires a little into the
# first word and the run-up was thrown away: on the demo's quiet Turkish
# recordings (-37 dBFS) the "S" of "Sürüm" rose -62 -> -53 dBFS in the 64 ms
# before the cut, and Whisper heard the non-word "Çürüm" on 2 of 3 plays.
# What fixed that was the LEVEL - clips raised 18 dB to the German voice's
# loudness gave "Sürüm" at every pre-roll length. The length itself only moved
# which other Turkish words flipped ("düzeltirim" -> "düzeldir", "duyuracak" ->
# "duyacak"); no length was clean on both recordings (8 Oct 2026). Kept because
# throwing away the start of a word is wrong by design, not because it measured
# better.
PREROLL_S = 0.3
PREROLL_CHUNKS = round(PREROLL_S * SR / CHUNK)

# How many earlier lines the translator sees, so "yayın" after "sürüm" is read
# as a release, not a broadcast. Two was enough on the scripted meeting.
TRANSLATE_CONTEXT = 2

# How much of the previous utterance to hand Whisper as context.
PROMPT_CHARS = 200

# A session has a language PAIR. Each utterance is shown in the language it
# was spoken in, plus the other one - so a speaker can check what the system
# understood and object on the spot.
LANGUAGES = ("tr", "en")

# How often a still-unfinished utterance is re-emitted as a PROVISIONAL line.
# Latency is otherwise MAX_UTTERANCE_S before anything appears at all, which is
# fine for watching a podcast and useless in a meeting: by the time a speaker
# reads "tomorrow" instead of "Wednesday" the conversation has moved on.
# 0 disables partials entirely.
REVISE_EVERY_S = 2.0
REVISE_SAMPLES = int(REVISE_EVERY_S * SR)

# Below this RMS an "utterance" is silence, and Whisper does not return nothing
# for silence - it returns something plausible from its training data. A 0.3s
# buffer of digital silence produced "Thank you." on one run and "Altyazı M.K."
# on another. Real speech here measures 0.04-0.16, so this sits far below
# anything a quiet speaker would produce and far above true silence.
MIN_RMS = 0.001

# Longest repeated run we look for when removing the overlap stutter.
DEDUP_WORDS = 8

def load_audio(path):
    """Decode any audio/video file to mono float32 at SR.

    silero's own read_audio() is unusable here: torchaudio 2.11 hands audio I/O
    to torchcodec, which isn't installed. ffmpeg is already a dependency
    (mlx-whisper shells out to it) and reads everything - mp3, m4a, mp4, wav.
    """
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg could not read {path!r}:\n{proc.stderr.decode().strip()}")

    # .copy() because frombuffer returns a read-only view of the pipe buffer,
    # and torch warns loudly every time it wraps a non-writable array.
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()


def _key(word):
    """A word reduced to what matters for comparison: no case, no punctuation."""
    return word.strip(".,!?;:\"'()[]\u2026").lower()


def drop_repeat(previous, said):
    """Remove words at the start of `said` that just repeat the end of `previous`.

    OVERLAP_S replays audio across a forced cut, so a word on the boundary gets
    transcribed twice ("...is Dr. Randy" / "Randy Gallisdell from Rutgers").
    Find the longest run of words that ends `previous` and starts `said`, and
    drop it. Comparison ignores case and punctuation, because Whisper often
    punctuates the same word differently on either side of a cut.
    """
    if not previous or not said:
        return said

    before = [_key(w) for w in previous.split()]
    words = said.split()
    after = [_key(w) for w in words]

    for n in range(min(DEDUP_WORDS, len(before), len(after)), 0, -1):
        if before[-n:] == after[:n]:
            return " ".join(words[n:])
    return said


class Utterance(NamedTuple):
    """One emission.

    `index` is stable across an utterance's provisional lines and its final
    one, so a display can REPLACE rather than append.

    `at` is where this utterance STARTS in the audio, in seconds - not when it
    was processed. Live they are the same; on a file they are not, and the
    transcript needs the audio position: attributing lines to people would work
    by running each participant's recording through separately and merging on
    time (not built).
    """
    index: int
    samples: object
    final: bool
    at: float


def is_silence(samples):
    """True if this buffer has no speech in it worth transcribing.

    The overlap carried across a cut can be silence on its own, and the VAD
    will happily close an utterance around it.
    """
    return float(np.sqrt(np.mean(np.square(samples, dtype=np.float32)))) < MIN_RMS


def tail(chunks, want):
    """The last `want` samples of `chunks`, as whole chunks (newest last)."""
    kept, total = [], 0
    for chunk in reversed(chunks):
        kept.append(chunk)
        total += len(chunk)
        if total >= want:
            break
    return list(reversed(kept))


def chunks_of(samples):
    """Slice a whole array into VAD-sized frames.

    The last partial frame (< CHUNK samples, so under 32 ms) is dropped: the
    VAD requires exactly CHUNK samples at this sample rate.
    """
    for i in range(0, len(samples) - CHUNK + 1, CHUNK):
        yield samples[i:i + CHUNK]


def utterances(chunks, revise_every=REVISE_SAMPLES):
    """Group a stream of frames into utterances.

    `chunks` is any iterable of float32 arrays of CHUNK samples - a file sliced
    by chunks_of(), or frames arriving live from a microphone. The VAD state
    machine is the same either way, which is the whole point: live capture is
    not a different algorithm, only a different source of frames.

    Yields Utterance(index, samples, final). While someone is still speaking it
    emits PROVISIONAL snapshots every `revise_every` samples, all carrying the
    same index, then a final one when the utterance closes. Pass revise_every=0
    for finals only - a file transcription has no reason to pay for revisions.
    """
    vad = VADIterator(
        load_silero_vad(),
        sampling_rate=SR,
        min_silence_duration_ms=MIN_SILENCE_MS,
    )
    buf = []
    before = deque(maxlen=PREROLL_CHUNKS)    # the run-up, kept while nobody speaks
    held = 0            # samples currently in buf, so we don't re-sum it each chunk
    speaking = False
    index = 1
    due = revise_every  # samples at which the next provisional is owed
    consumed = 0        # samples seen, so an utterance knows where it began
    began = 0.0

    for chunk in chunks:
        consumed += len(chunk)
        event = vad(chunk)

        if event and "start" in event:
            speaking = True
            buf = list(before) + [chunk]
            held = sum(len(c) for c in buf)
            due = revise_every
            began = (consumed - held) / SR
            continue

        if not speaking:
            before.append(chunk)

        if speaking:
            buf.append(chunk)
            held += len(chunk)

            if revise_every and held >= due and held < MAX_SAMPLES:
                # Same index as the final that will follow: the display replaces
                # this line rather than adding one.
                block = np.concatenate(buf)
                if not is_silence(block):
                    yield Utterance(index, block, False, began)
                due = held + revise_every

            if held >= MAX_SAMPLES:
                block = np.concatenate(buf)
                if not is_silence(block):
                    yield Utterance(index, block, True, began)
                    index += 1
                # speaking stays True: the speech goes on, only the cut happened.
                # Carry the tail over so the next utterance starts mid-word-safe.
                buf = tail(buf, OVERLAP_SAMPLES)
                held = sum(len(c) for c in buf)
                due = held + revise_every
                began = (consumed - held) / SR

        if event and "end" in event:
            speaking = False
            if buf:     # may be empty if a forced cut just fired on this chunk
                block = np.concatenate(buf)
                if not is_silence(block):
                    yield Utterance(index, block, True, began)
                    index += 1
            buf, held = [], 0
            before.clear()      # what follows an utterance is not the next one's run-up
            due = revise_every

    if buf:
        block = np.concatenate(buf)
        if not is_silence(block):
            yield Utterance(index, block, True, began)


def translator(engine="llm", host=None, model=None):
    """Pick a translator. Both expose to_turkish(text, src).

    "llm"  - Ollama, ~1.3s/line, right about terminology.
    "nllb" - NLLB-200-600M, ~0.2s/line, but "age reversal" -> "yas degisimi"
             and "neuroscience" -> "Noroloji". Kept for when speed matters more
             than getting technical vocabulary right.

    Imported lazily so a run only loads the models it actually uses.
    """
    if engine == "nllb":
        import facts
        import translate

        # Any pair now, and fact-checked like the LLM: NLLB rendered "16 Uhr"
        # as "4'e" (12-hour), so a line whose numbers change is shown as the
        # original alone rather than with a wrong time.
        return facts.checked(lambda text, src, target, context=None:
                             translate.translate(text, src, target))

    import facts
    import translate_llm
    translate_llm.configure(host, model)

    def nllb(text, src, target):
        import translate         # loaded only when the LLM gets a fact wrong
        return translate.translate(text, src, target)

    # The LLM wrote "Salı" for "Mittwoch" once, live, on screen. facts.checked
    # keeps any line whose days or numbers changed from being shown.
    return facts.checked(lambda text, src, target, context=None:
                         translate_llm.translate(text, target, src, context),
                         fallback=nllb)


_warned = set()


def _warn_once(message):
    """Say it the first time only - a per-utterance failure would flood the screen."""
    if message not in _warned:
        _warned.add(message)
        print(message, file=sys.stderr)


def rough_translator():
    """NLLB, for lines that are about to be replaced.

    ~0.2s against the LLM's ~1.3s. It is worse - "age reversal" comes back as
    "yas degisimi" - but a provisional line only has to be roughly right for two
    seconds. The final one, from the LLM, corrects it.

    Returns None if NLLB will not load, in which case provisionals fall back to
    showing the original text alone.
    """
    try:
        import translate
        return translate.translate
    except Exception as unavailable:      # noqa: BLE001 - never break the stream
        print(f"[rough] NLLB unavailable ({unavailable}); "
              f"provisional lines will show the original only", file=sys.stderr)
        return None


def transcript_line(key, text, source, said_lang=None, other_lang=None, final=True,
                    at=None):
    """Default sink: a scrolling transcript. Right for a file, wrong for live."""
    if not final:
        return          # a scrolling log would just repeat itself three times
    print(f"{key:3d}. [{said_lang or '--'}] {source}")
    print(f"     [{other_lang or '--'}] {text}\n", flush=True)


def subtitle(chunks, lock_language=False, show=transcript_line, translate_fn=None,
             languages=None, revise=True, rough_fn=None):
    """Transcribe and translate a stream of frames, printing as it goes.

    Ends when `chunks` runs out (a file) or never (a live device). Everything
    here is source-agnostic: a file and a live device are just two sources of frames.

    translate_fn defaults to the LLM translator; see translator().

    `show(key, turkish, source)` is where finished subtitles go. The pipeline
    does not know whether that is a terminal, a caption window or a browser
    page - so a new screen is a new sink, not a rewrite.

    By default the source language is detected on EVERY utterance. Locking it
    after the first one saves ~170ms per utterance (373ms -> 200ms), which is
    nothing against a 4s cap, and the failure mode is severe: pinned to the
    wrong language Whisper stops transcribing and hallucinates stock phrases
    ("abone ol", "izlediginiz icin tesekkur ederim"), while NLLB decides the
    text is already Turkish and returns it untranslated. Lock only when you
    know the source is single-language.
    """
    translate_fn = translate_fn or translator()
    # Resolved here, not as a default argument: --languages rebinds the
    # module global, and a default would have been frozen at def time.
    languages = languages or LANGUAGES
    locked = None
    context = None
    context_lang = None
    # The last few FINAL lines, as said, for the translator - not Whisper's
    # prompt above, which is one language's tail. See translate_llm.GLOSSARY.
    recent = []

    for utterance in utterances(chunks, revise_every=REVISE_SAMPLES if revise else 0):
        # Provisionals go without the prompt. It only helps a sentence continue,
        # which a line about to be replaced does not need - and after a language
        # switch the prompt forces a second Whisper pass (below). Paid on every
        # provisional of a two-language meeting, that doubled the work and the
        # lag grew turn by turn: 2s after the speaker stopped, then 10s.
        prompt = context if utterance.final else None
        result = transcribe.transcribe_file(
            utterance.samples, language=locked, initial_prompt=prompt
        )
        language = result["language"]

        if prompt and language != context_lang:
            # The speaker changed language. A prompt in the PREVIOUS language
            # does not merely fail to help - it drags the output into that
            # language: a Turkish line after a Greek one came back as
            # "Υπότιτλοι AUTHORWAVE", and an English one as multi-script
            # gibberish. Detection stays right even when the text is destroyed,
            # which is what makes this recoverable: transcribe again with no
            # prompt at all. Costs one extra pass, and only on a switch.
            result = transcribe.transcribe_file(utterance.samples, language=locked)
            language = result["language"]
        if lock_language and locked is None:
            locked = language
            print(f"language locked: {language}\n")

        # Whisper marks a continuation with a leading ellipsis; it is noise on screen.
        said = result["text"].strip().lstrip("\u2026. ").strip()
        said = drop_repeat(context, said)
        if not said:
            continue        # no speech, or the whole utterance was overlap

        target = other(language, languages)

        if not utterance.final:
            # A provisional carries the ORIGINAL - the half a speaker checks
            # against what they actually said - plus a ROUGH translation from
            # NLLB. Waiting for the LLM would cost 1.3s on a line that is about
            # to be replaced anyway, and a Turkish reader would sit through the
            # whole utterance with nothing to read.
            rough = ""
            if rough_fn:
                try:
                    rough = rough_fn(said, language, target)
                except Exception as failed:     # noqa: BLE001
                    # A rough line is a bonus, never a dependency: an unknown
                    # language or a model hiccup must not stop the meeting.
                    _warn_once(f"[rough] {failed}")
            show(utterance.index, rough, said, said_lang=language,
                 other_lang=target if rough else None, final=False,
                 at=utterance.at)
            continue

        # Hand the tail forward: the next utterance often starts mid-sentence,
        # and this is what lets Whisper continue it instead of guessing cold.
        # Finals only - a provisional would poison the prompt with half a clause.
        context = said[-PROMPT_CHARS:]
        context_lang = language

        show(utterance.index, translate_fn(said, language, target, context=recent[-TRANSLATE_CONTEXT:]),
             said, said_lang=language, other_lang=target, final=True, at=utterance.at)
        recent.append(f"({language}) {said}")


def captions_sink():
    """A fixed caption area: new subtitles replace the old instead of scrolling.

    Leaves nothing in the scrollback, which is right for watching and useless
    for reviewing - see with_transcript() for the record.
    """
    import display

    board = display.Captions()
    screen = display.Terminal(board)

    def show(key, text, source, said_lang=None, other_lang=None, final=True, at=None):
        board.show(key, text, source=source)
        screen.draw()

    return show


def titles_sink(show, path, style="both"):
    """Also write the current caption to a plain text file, overwritten each time.

    For a titler that watches a file - Wirecast and friends can render that
    natively, with real alpha and their own fonts, so no browser and no chroma
    key are involved at all.

    style picks what goes in the file, because a titler may only render the
    first line of it:
      both        what was said, then the translation, on two lines (default)
      one-line    the same, joined with a dash, so a single-line title shows both
      translation the translation alone
      original    what was said alone
    """
    if not path:
        return show

    print(f"titles     {path}   ({style})   <- point the title source at this file")

    def wrapped(key, text, said, said_lang=None, other_lang=None, final=True, at=None):
        show(key, text, said, said_lang=said_lang, other_lang=other_lang,
             final=final, at=at)
        # Written whole and replaced, never appended: a titler shows the file's
        # contents, so the file must only ever hold what is on screen NOW.
        if style == "translation":
            lines = [text or said]
        elif style == "original":
            lines = [said]
        elif style == "one-line":
            lines = [" — ".join([said] + ([text] if text else []))]
        else:
            lines = [said] + ([text] if text else [])
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("\n".join(lines) + "\n")
        except OSError:
            pass        # a titler holding the file open must not stop the meeting

    return wrapped


def with_transcript(show, log_path, languages=None, source=None):
    """Wrap any sink so every FINAL line also lands in the transcript.

    One writer for every surface: the terminal, the caption view and the web
    page all record identically, and none of them has to know how. Provisional
    lines are never written - the record is the corrected version.
    """
    if not log_path:
        return show

    import transcript
    record = transcript.Transcript(log_path, languages=languages, source=source)
    print(f"transcript {log_path}")

    def wrapped(key, text, said, said_lang=None, other_lang=None, final=True, at=None):
        show(key, text, said, said_lang=said_lang, other_lang=other_lang,
             final=final, at=at)
        if final:
            record.add(said_lang, said, other_lang, text, at=at)

    return wrapped


WEB_SERVER = None       # set by web_sink(), so __main__ can keep serving


DEFAULT_PORT = 8770     # kept in step with web.PORT


def web_sink(port, lines=1):
    """Serve the participant page.

    The asymmetry is deliberate: everyone gets to VERIFY (the last RETAIN_S
    seconds), only this machine keeps the RECORD - see with_transcript().
    """
    global WEB_SERVER
    import display
    import web

    server = WEB_SERVER = web.CaptionServer(port=port, lines=lines).start()
    address = web.lan_address()
    print(f"captions   http://{address}:{server.port}       <- share this in the chat")
    print(f"wirecast   http://{address}:{server.port}/?key=green&size=1.4")
    print(f"           last {int(display.RETAIN_S)}s only; the full record stays here\n")
    def show(key, text, source, said_lang=None, other_lang=None, final=True, at=None):
        server.show(key, text, source=source, said_lang=said_lang,
                    other_lang=other_lang, final=final)
        if final:       # the console echo keeps finals only
            print(f"{key:3d}. [{said_lang}] {source}\n     [{other_lang}] {text}\n",
                  flush=True)

    return show


def main(path, show, lock_language=False, translate_fn=None, rough_fn=None,
         revise=False):
    audio = load_audio(path)
    print(f"{path}: {len(audio) / SR:.1f}s")
    subtitle(chunks_of(audio), lock_language=lock_language, translate_fn=translate_fn,
             revise=revise, rough_fn=rough_fn, show=show)


def recorded(frames, path):
    """Pass frames through unchanged, keeping them in a 16 kHz WAV as well.

    The small path's notes start from a SECOND transcription: Whisper
    large-v3-turbo made no word errors on the scripted meeting against small's
    6.8%, but runs at 1.3x real time on a CPU - too slow live, fine after the
    meeting. So the audio is kept: stream.py meeting.wav --cpu
    --whisper large-v3-turbo --log clean.txt.
    """
    import wave
    every = 60 * SR                 # say how long it has been recording, each minute
    written = 0
    with wave.open(path, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SR)
        for frame in frames:
            out.writeframes((np.clip(frame, -1, 1) * 32767).astype(np.int16).tobytes())
            written += len(frame)
            # A forgotten --record kept every sound on this machine for 4 h 41 min
            # before anyone noticed. It records until Ctrl-C, so it says so.
            if written % every < len(frame):
                print(f"[record] {written // every} min so far in {path} - Ctrl-C to stop",
                      file=sys.stderr, flush=True)
            yield frame


def live(show, device=None, lock_language=False, translate_fn=None, rough_fn=None,
         record=None):
    # Imported here, not at the top: capture.py imports SR and CHUNK from this
    # module, so a module-level import would be circular - and a file run has no
    # reason to touch an audio device at all.
    import capture

    print(f"live from {device or 'default input'} - Ctrl-C to stop\n")
    frames = capture.frames(device)
    if record:
        print(f"recording  {record}   <- for a cleaner transcript after the meeting\n")
        frames = recorded(frames, record)
    try:
        subtitle(frames, lock_language=lock_language,
                 translate_fn=translate_fn, rough_fn=rough_fn, show=show)
    except KeyboardInterrupt:
        frames.close()          # finishes the WAV header
        print("\nstopped.")


def _take(argv, flag):
    """Pull '--flag VALUE' out of argv, returning (value, remaining argv)."""
    if flag not in argv:
        return None, argv
    at = argv.index(flag)
    return argv[at + 1], argv[:at] + argv[at + 2:]


if __name__ == "__main__":
    argv = sys.argv[1:]
    log_path, argv = _take(argv, "--log")
    port, argv = _take(argv, "--port")
    host, argv = _take(argv, "--ollama")
    model, argv = _take(argv, "--model")
    pair, argv = _take(argv, "--languages")
    lines, argv = _take(argv, "--lines")
    titles, argv = _take(argv, "--titles")
    titles_style, argv = _take(argv, "--titles-style")
    whisper_size, argv = _take(argv, "--whisper")
    record_path, argv = _take(argv, "--record")
    glossary_path, argv = _take(argv, "--glossary")
    if glossary_path:
        import translate_llm
        translate_llm.GLOSSARY = open(glossary_path, encoding="utf-8").read().strip()
        print(f"glossary   {glossary_path}   ({len(translate_llm.GLOSSARY.splitlines())} terms)")
    if pair:
        LANGUAGES = tuple(pair.split(",")[:2])

    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    is_live = "--live" in flags
    lock = "--lock" in flags

    # Everything on the CPU: faster-whisper (small unless --whisper says
    # otherwise) + NLLB, no LLM while people talk. An experiment, kept for the
    # measurements: it keeps up (final line 3.8 s after the speaker stops), but
    # Whisper small got 20.8% of Turkish words wrong - live Turkish captions
    # were unusable. See DECISIONS.md.
    if "--cpu" in flags:
        import torch
        import translate
        transcribe.configure("faster-whisper", whisper_size or "small")
        translate.DEVICE = "cpu"
        torch.set_num_threads(transcribe.threads())
        flags.add("--nllb")
    elif whisper_size:
        transcribe.configure("mlx", whisper_size)     # e.g. --whisper large-v3
    print(f"whisper    {transcribe.MODEL if transcribe.ENGINE == 'mlx' else transcribe.SIZE}")

    translate_fn = translator("nllb" if "--nllb" in flags else "llm", host, model)
    # Rough provisional translation is on by default; --no-rough turns it off
    # (one less model resident, and the way to measure what it is worth).
    rough_fn = None if "--no-rough" in flags else rough_translator()

    # Pick the surface. Live defaults to the caption view because a scrolling
    # transcript is unreadable at speaking pace; a file defaults to scrolling
    # because captions race past at 10x realtime.
    if "--web" in flags:
        show = web_sink(int(port or DEFAULT_PORT), lines=int(lines or 1))
    elif "--captions" in flags or (is_live and "--transcript" not in flags):
        show = captions_sink()
    else:
        show = transcript_line

    source = (args[0] if args else "default input") if is_live else (args[0] if args else "")
    show = titles_sink(show, titles, style=titles_style or "both")
    show = with_transcript(show, log_path, languages=LANGUAGES, source=source)

    if is_live:
        live(show, args[0] if args else None, lock_language=lock,
             translate_fn=translate_fn, rough_fn=rough_fn, record=record_path)
    else:
        main(args[0], show, lock_language=lock, translate_fn=translate_fn,
             rough_fn=rough_fn, revise="--web" in flags)

        # A file ends; the page should not. Without this the process exits the
        # moment the audio runs out and takes the daemon server thread with it,
        # so nobody can look at what was just captioned.
        if WEB_SERVER is not None:
            print("\nfile finished - captions still served; Ctrl-C to stop")
            try:
                threading.Event().wait()
            except KeyboardInterrupt:
                pass
