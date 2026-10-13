# Models — what proved "good enough"

Everything runs **locally**. A single modern GPU (here, one with 32 GB of memory) handles the
daily work; a slower CPU-only setup works for a smaller run. No cloud model, no per-article cost.

What this project uses (all open-weight, swap freely):

| Job | Model | Notes |
|---|---|---|
| Read & shortlist | **Qwen2.5-32B** | reads the day's pool, surfaces candidates per topic |
| Draft / translate / critique | **Qwen3.8-27B** | headlines, "why it matters", the critique; fast on one GPU |
| Cross-language dedup | **bge-m3** | multilingual embeddings — catches the same story across languages |
| Cover art | **FLUX.1-dev** | metaphorical covers; an fp8 build on the GPU, a 4-bit build on a Mac |

**The lesson:** a few years ago this needed the cloud; today a resident ~27–32B model does the
daily editorial work well, and the quality gap to the biggest models is small for this task. If
your hardware is smaller, start with an 8–16 GB card and a 7–8B model — slower, but it works. Run
models through something simple (e.g. Ollama) so swapping one out is a config change.
