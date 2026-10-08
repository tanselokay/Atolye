# What we measured, and what we do not know

> _Generated with Claude (Anthropic) · Bu belge Claude (Anthropic) ile üretildi._

> **Proof of concept (kavram kanıtı), not a product.** Everything below was
> measured on one scripted meeting: read from a script, by one real voice and
> one synthetic voice (earlier runs: synthetic voices only). It shows the
> pieces can be put together and run on one machine; it does not show that
> live captioning or meeting notes work in a real meeting - including the
> setup in the demo video. Read the numbers as lab notes.

## What was tested

One project-review meeting: 18 short turns, one speaker in Turkish, one in
German, written in advance. In the demo video the Turkish is the author's own
voice, read from the script and recorded at home on one microphone; the German
is a synthetic voice (Piper `de_DE-thorsten-high`, CC0). The measurements in
the lab notes below were made earlier, on the same script spoken by synthetic
voices only (Speechelo; macOS voices for the three-language test). The audio
was played into Loopback and captured live, on an M4 Max MacBook Pro with 64 GB.

That is the easiest case there is:

- **clean pauses** between turns, set by a script, so every sentence is cut
  where it ends;
- **no overlap, no interruptions, no hesitation** - nobody says "ehm", starts
  again, or talks over someone else;
- **one voice per language**, no accent; the Turkish one with a room and a
  microphone, the German one synthetic;
- **3-second pauses** put between turns so the translation appears before the
  reply;
- **short sentences**, never long enough to hit the 6-second forced cut;
- **no names, no jargon** beyond "release notes".

Real conversations have all of these. Each one is a known way for speech
recognition to fail, and **none of them was tested here.** One informal run on
a podcast (9 September, English to Turkish) ran without errors on screen; it
was not measured.

## What the demo video shows

| Step | Model | Where |
|---|---|---|
| Speech to text | Whisper large-v3-turbo (MLX) | Apple GPU, 2.5 GB |
| Draft lines | NLLB-200 600M | Apple GPU |
| Final translation | qwen3.8 27B, IQ4_XS quant (`batiai/qwen3.8-27b:iq4`) | Apple GPU, 16.5 GB |
| Notes | the same 27B | Apple GPU |

About 22 GB of GPU memory, Apple Silicon only.

With the real Turkish voice (8 Oct 2026): every day and time right; Whisper
wrote a wrong word on four of the ten Turkish lines ("planlarından", a stray
"bu", "müşteriyi ... duyacak", "küçüğü") and heard German "bis" (by) as
"des"; the German translation still carried the meaning of every Turkish line;
in Turkish and in the notes the "by Wednesday 16:00" deadline became "at
16:00". The video is left as it is. With synthetic voices only, earlier, all 21
lines were right and final captions came 1.2-2.9 s after the speaker stopped.
That is all it shows.

The Turkish recordings were raised 18 dB to the German voice's level: they
were 19 dB quieter, and at that level the first word "Sürüm" came out as the
non-word "Çürüm" on 2 of 3 plays. In a call a quiet speaker is asked to speak
up; a pipeline that needs its audio edited is not a fix, and a real meeting is
far less controlled than this.

```
stream.py --live loopback --web --languages tr,de --glossary glossary.txt --log t.txt
notes.py t.txt --glossary glossary.txt
```

## Design fixes for the real voice, and what they did not fix

Measured by replaying the recorded audio through the pipeline (the replay
reproduces a live take word for word); where a setting was run twice, both
runs were identical.

- **Translation context and a meeting glossary.** The translator sees the two
  previous lines and a short glossary (`--glossary`, one `term = Begriff` per
  line). The first take turned "geri dönüş seçeneği / yayın" (rollback option /
  release) into "Rückgabeoption nach der Ausstrahlung" (return option after the
  broadcast); with context and glossary: "Rollback-Option nach der
  Veröffentlichung". **The glossary was written after seeing the first take's
  mistakes** - "kapsam = Umfang" is why the German survives "küçüğü". In a real
  meeting it has to be written in advance and only helps with terms foreseen.
- **Pre-roll.** The voice detector fires a little into the first word and the
  audio before it was thrown away; on the quiet recordings the "S" of "Sürüm"
  was in those 64 ms. 0.3 s before the cut is now kept. What actually fixed
  "Sürüm" was the level: at matched level it was right at every pre-roll
  length (0, 0.1, 0.2, 0.3 s), and the length only moved which other Turkish
  word flipped ("düzeldir" for "düzeltirim", "duyacak" for "duyuracak"). No
  length was clean on both recordings; 0.3 s is kept because throwing away the
  start of a word is wrong by design, not because it measured better.
- **Whisper vocabulary prompt (not built).** Giving Whisper the glossary's
  terms in the utterance's language fixed "Çürüm" 3 of 3 but dropped
  "Haklısın" (you're right) from the next correction, 2 of 2.
- **A bigger model.** Full Whisper large-v3 (`--whisper large-v3`), replaying
  the demo take: fixed "bu", "müşteriyi" and "duyacak"; did not fix "küçüğü" or
  "des"; ~1.6 s per line against turbo's ~1.2 s. On the earlier recording of the
  same clips it broke "düzeltirim". Better, not right. Not run live.
- **Not fixable by confidence.** On "küçüğü" Whisper is *most* confident where
  it is wrong, so a low-confidence flag would not catch it. The design answer
  is that speakers see their own words on screen and repeat when they are
  wrong - which is asking a lot of someone who is talking.

## Other speech models on the same recording

Is turbo the best that runs locally? An independent Turkish ranking (Emre
Akgül's leaderboard: the same FLEURS read speech and the same scoring for every
model) says: Whisper large-v3 5.66% word errors, large-v3-turbo 6.07%, Meta
Omnilingual 7B 6.09%, Qwen3-ASR 1.7B 8.46%. Among models that run locally,
Whisper is the best with independent evidence.
https://huggingface.co/spaces/EmreAkgul/Turkish-transcription-leaderboard

We replayed the demo take (same 20 utterances, same cuts) through four more.
Wrongly written words on the 10 Turkish lines (case, punctuation, digits vs.
words not counted), the two words that change the meaning, and time per
sentence:

| Model | Wrong words | "küçük" | German "bis" | s / sentence |
|---|---|---|---|---|
| large-v3-turbo (the video) | 5: planlarından, bu, müşteriyi, duyacak, küçüğü | wrong | "des" | 0.7 |
| large-v3 | 2: planlandan, küçüğü | wrong | "des" | 1.6 (other Mac) |
| BuzzASR (large-v3 Turkish fine-tune) | 2: planlandan, küçüğü | wrong | "des" | 1.1 |
| TurkMedSTT (large-v3 Turkish fine-tune) | 3: planlandan, düzeldir, küçüğü | wrong | "des" | 1.2 |
| Qwen3-ASR 1.7B | 4: Tesel, Tesr, sorununu, mız | right | right | 0.5 |

- The two Turkish fine-tunes beat large-v3 in their own measurements, not on
  ours, and are not on the independent ranking. Neither broke the German.
- Qwen3-ASR is the only one that got both meaning-changing words right, and it
  garbled the subject "Testler" twice. Differently wrong, not better.
- **No model was clean, and they were wrong in different places.** Every error
  of turbo and of Qwen3-ASR sat on a word where the two disagreed; every line
  they agreed on was right. One meeting, 19 lines - a lab note. Confidence could
  not flag "küçüğü" (Whisper was most confident there); a second, different
  model did. Not built.

Fine-tunes were converted to MLX with Apple's `mlx-examples/whisper/convert.py`
(safetensors only); Qwen3-ASR ran through the `qwen-asr` package on the Apple
GPU, outside Yazoğlum.

## The safeguard: facts are checked in code

Every model we tried, the 27B included, at some point changed a day or a time
while translating: "Mittwoch" (Wednesday) became "Salı" (Tuesday), a
"yesterday" appeared that nobody said, 16:00 became "4". Asking a model to be
careful did not stop it. So `facts.py` compares each translation with what was
said - weekdays, yesterday / today / tomorrow, parts of the day, and numbers
in digits or words, in Turkish, German and English - and:

- repairs a swapped weekday, or a time read on a 12-hour clock, from the
  original;
- otherwise uses another translator, or shows the line untranslated. A line
  in its original language is incomplete; a wrong day is a false record.

`notes.py` uses the same check, and flags any day or number in the notes that
nobody said.

**What it cannot catch:** a fact that was said, but for something else (a
deadline moved to the wrong task); a decision that was never made (a model
once turned an open question into one); anything that is not a day, a time or
a number. **Read the notes against the transcript before sending them.**

---

## Lab notes: smaller setups

We measured how far the same pipeline gets with less memory, to see where it
breaks. These are observations on the scripted meeting, **not
recommendations**: if the demo setup is unproven on real speech, the smaller
ones are more so.

### Speech to text

Whisper on the CPU (faster-whisper, int8), the meeting cut into sentences
exactly as live, word error rate:

| | Turkish | German | English | Time / real time |
|---|---|---|---|---|
| small | **20.8%** | 3.0% | 3.4% | 0.26x |
| medium | 2.3% | 1.8% | 4.0% | 0.80x |
| large-v3-turbo | 1.5% | 0.6% | 4.5% | 1.31x |

Same 18 sentences in each language, one synthetic voice family (English errors
are mostly "1400 hours" written for "14:00"). **The weakness is Turkish, not
model size:** small is fine for German and English and turns Turkish into
nonsense ("Cumás-ı Atom 4'te" for "cuma saat 14'te"). Whisper was trained on
far less Turkish than English or German. Two Turkish fine-tunes of small did
worse (24% and 45%; one invented whole sentences). Medium and turbo are good
enough on Turkish but cannot keep up live on a CPU - the lag grew to 186 s.

On the Apple GPU, turbo keeps up easily (30 s of audio in 2.3 s, 2.5 GB). It is
the translation model, not Whisper, that needs the memory.

### Translation

Raw day/number errors, before `facts.py`:

| Model | Where | Size loaded | s / line | Errors |
|---|---|---|---|---|
| qwen3.8 27B IQ4_XS | GPU | 16.5 GB | ~1.4 | 0/90 on 5 Oct, 2/54 on 6 Oct |
| qwen3.8 27B Q4_K_M | GPU | 17.4 GB | ~1.9 | 8/90 |
| TranslateGemma 12B | GPU | 9.0 GB | 0.61 | 0/21 |
| Aya Expanse 8B | GPU | 6.4 GB | 0.26 | 0/54 |
| TranslateGemma 4B | GPU | 3.3 GB | 0.25 | 4/21 |
| NLLB-200 600M | GPU / CPU | ~2.4 GB | 0.24 | 1/18 |
| Opus-MT, tr<->de through English | CPU | ~0.3 GB each | 0.21 | 2/18 |
| qwen3.5 9B / 4B, qwen2.5 14B / 7B | GPU | 3-9 GB | - | wrong weekdays every run |

Facts are only half of it. Line by line on the same 21 sentences, the 27B read
better than Aya 8B on 8 lines and worse on 3; most of the gap is German to
Turkish, where the smaller models translate word by word ("Düşündüm ki ...
dedik" for "Ich dachte ...", "İyi" for "Gut"). TranslateGemma 12B wrote more
natural Turkish than Aya but made errors Aya did not ("demiştiğimiz", "nochmals"
for "separately"). NLLB is literal and sometimes simply wrong ("Augenlicht",
eyesight, for "görsel sorun"). One line - "geri dönüş seçeneği" (rollback
option) - no model translated correctly.

What a smaller setup gave on this meeting, roughly:

| GPU memory | Translation | Observed |
|---|---|---|
| ~6 GB | turbo + NLLB | literal, sometimes wrong wording; facts held |
| ~11 GB | turbo + Aya 8B | correct but clumsy German to Turkish |
| ~22 GB | turbo + 27B | the most natural; the demo |
| CPU only | small + NLLB | Turkish captions unusable |

Each of these ran live on this meeting once or twice. Only the 22 GB one is
the demo.

### Notes

Written after the meeting, so speed does not matter. With the 27B and with
Aya 8B, the notes from the scripted meeting matched it in every run we checked
- at temperature 0.1. At 0.3, Aya turned the open question into a decision in
1 run of 5. qwen2.5 7B moved a deadline to the wrong day.

A line whose live translation was withheld is translated again by the notes
model, under the same check, before the notes are written - otherwise that
line, a deadline in German, was left out of every set of notes.

---

## Mistakes we made measuring

Worth more than the numbers, if you measure anything like this yourself:

- **Whole clips flatter.** Each test clip held two sentences; Whisper small got
  them right. Cut into single sentences, as live, it did not. Measure the path
  the audio really takes.
- **Clean conversions flatter.** Clips converted with ffmpeg sounded better to
  Whisper than the same clips captured through Loopback, because asking the Mac
  for 16 kHz let it resample with a filter that removed half the energy between
  6 and 8 kHz, where "t" and "k" are. Yazoğlum now captures at the device's own
  rate and converts with soxr.
- **A clean run is not a property.** The 27B made 0 errors in 90 lines one day
  and 2 in 54 the next. Run more than once.
- **Check the screen, not the log.** For two takes the transcript was right
  and the page was not: a rewrite held back for readability kept the draft's
  unfinished original next to the final translation.
- **A quiet speaker is a different test.** The real Turkish voice arrived 19 dB
  below the synthetic German one; half of what looked like Turkish being hard
  was level.
- **Every change flips some other word.** On ten Turkish lines, each setting
  that fixed one word broke another. Choosing a constant on that is fitting
  noise; a fix needs a reason that holds without the measurement.

## Not tested

Spontaneous speech (the real voice read a script). More than two people.
Overlapping speech. Accents, noise, other microphones. Long monologues. Speaker names (captions show the language, not the
person). A real Zoom call. Windows, Linux, NVIDIA GPUs, Macs with less memory.
Anything over three minutes.

`--record` records everything that reaches the input until it is stopped with
Ctrl-C; it prints the running length every minute. Recording a meeting has
consent rules that vary by country.
