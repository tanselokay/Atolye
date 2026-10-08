# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""Live audio capture: turn a microphone or Loopback into VAD-sized frames.

stream.utterances() consumes an iterable of frames and does not care where
they come from. This module is that source for live audio, exactly as
stream.chunks_of() is for a file.
"""

import queue
import sys

import numpy as np
import sounddevice as sd

from stream import CHUNK, SR


def find_device(wanted=None):
    """Resolve an input device: an index, a name fragment, or None for the default.

    Names are matched case-insensitively on a substring, so "loopback" is
    enough for "Loopback Audio".
    """
    if wanted is None:
        return None                      # sounddevice picks the system default
    if isinstance(wanted, int) or str(wanted).isdigit():
        return int(wanted)

    needle = str(wanted).lower()
    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0 and needle in device["name"].lower():
            return index
    raise ValueError(f"no input device matching {wanted!r}")


def inputs():
    """Every device that can capture, as (index, name, channels)."""
    return [(i, d["name"], d["max_input_channels"])
            for i, d in enumerate(sd.query_devices()) if d["max_input_channels"] > 0]


def frames(device=None, channels=1):
    """Yield CHUNK-sized mono float32 frames at SR from a live input, endlessly.

    The callback runs on CoreAudio's realtime audio thread. It must never block
    or do real work, or the capture glitches - so it does the one cheap thing,
    copying the buffer into a queue, and everything else happens on this side.

    The device is opened at its OWN rate and converted to 16 kHz here, with
    soxr. Asking CoreAudio for 16 kHz directly let it resample with a cheaper
    filter: the Loopback recording had half the energy at 6-8 kHz of the same
    clip converted by ffmpeg, which is where "t" and "k" live. Whisper large
    did not care; Whisper small heard "Kritik hatalar" as "süreti katağlar",
    and dulling a clean clip the same way reproduced it.

    Note the first call will make macOS raise a microphone-permission dialog,
    which blocks until answered.
    """
    import soxr

    index = find_device(device)
    info = sd.query_devices(index if index is not None else sd.default.device[0])
    rate = int(info["default_samplerate"])
    incoming = queue.Queue()

    def callback(indata, frame_count, time_info, status):
        if status:
            print(f"[audio] {status}", file=sys.stderr)
        # PortAudio reuses indata after this returns, so copy or lose it.
        incoming.put(indata.copy())

    resampler = soxr.ResampleStream(rate, SR, 1, dtype="float32", quality="HQ")
    pending = np.zeros(0, dtype=np.float32)

    with sd.InputStream(device=index, samplerate=rate, blocksize=round(CHUNK * rate / SR),
                        channels=channels, dtype="float32", callback=callback):
        print(f"listening on: {info['name']}  ({rate} Hz -> {SR} Hz, {channels} ch)",
              file=sys.stderr)

        while True:
            block = incoming.get()
            # Down to mono: one channel is already there, more get averaged so a
            # source that only fills the left channel is not lost.
            mono = (block[:, 0] if block.shape[1] == 1
                    else block.mean(axis=1)).astype(np.float32)
            pending = np.concatenate([pending, resampler.resample_chunk(mono)])
            # The VAD takes exactly CHUNK samples; the resampler does not
            # return round numbers, so hand them on in CHUNK-sized pieces.
            while len(pending) >= CHUNK:
                yield pending[:CHUNK]
                pending = pending[CHUNK:]


if __name__ == "__main__":
    for index, name, channels in inputs():
        print(f"  [{index:2d}] {name}   ({channels} ch)")
