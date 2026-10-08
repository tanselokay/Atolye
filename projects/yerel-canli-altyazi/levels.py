# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""Is any audio actually reaching the capture device?

The pipeline is silent in exactly the same way whether nobody is speaking or
the device is routed wrong, and telling those apart at the start of a meeting
is not the moment to start guessing.

    levels.py            # default input
    levels.py loopback   # by name fragment, or an index
"""

import sys
import time

import numpy as np
import sounddevice as sd

import capture

SECONDS = 8


def main(argv):
    device = capture.find_device(argv[0]) if argv else None
    name = sd.query_devices(device if device is not None
                            else sd.default.device[0])["name"]
    channels = min(2, sd.query_devices(device if device is not None
                                       else sd.default.device[0])["max_input_channels"])
    print(f"listening on: {name}\nPlay something, or talk, for {SECONDS}s\n")

    levels = []
    with sd.InputStream(device=device, samplerate=16000, blocksize=512,
                        channels=channels, dtype="float32",
                        callback=lambda d, *_: levels.append(float(np.sqrt(np.mean(d ** 2))))):
        for second in range(SECONDS):
            time.sleep(1)
            peak = max(levels[-31:] or [0])
            print(f"  {second + 1}s  {peak:.5f}  {'#' * min(46, int(peak * 400))}")

    top = max(levels) if levels else 0
    print()
    if top < 0.0005:
        print(f"SILENT (peak {top:.6f}). Nothing is reaching this device.")
        print("Loopback: open Loopback.app, add the app (zoom.us) under Sources,")
        print("and set your headphones under Monitors so you still hear it.")
        return 1
    print(f"AUDIO PRESENT (peak {top:.5f}) - ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
