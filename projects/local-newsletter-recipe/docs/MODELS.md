# Modeller — "yeterince iyi" olan / Models — what proved "good enough"

Her şey **yerelde** çalışır. Günlük işi tek bir modern GPU (burada 32 GB bellekli bir kart) görür;
daha yavaş, yalnızca-CPU bir kurulum küçük bir çalışma için yeterli. Bulut modeli yok, haber başına
maliyet yok.

_Everything runs **locally**. A single modern GPU (here, one with 32 GB of memory) handles the daily
work; a slower CPU-only setup works for a smaller run. No cloud model, no per-article cost._

Bu projenin kullandıkları — hepsi açık ağırlıklı, serbestçe değiştir / What this project uses, all
open-weight, swap freely:

| İş / Job | Model | Not / Notes |
|---|---|---|
| Oku ve ele / Read & shortlist | **Qwen2.5-32B** | günün havuzunu okur, konu başına aday çıkarır / reads the pool, surfaces candidates per topic |
| Taslak · çeviri · kritik / Draft · translate · critique | **Qwen3.8-27B** | başlık, "neden önemli", kritik; tek GPU'da hızlı / headlines, "why it matters", the critique; fast on one GPU |
| Diller-arası tekilleştirme / Cross-language dedup | **bge-m3** | çok dilli gömme — aynı haberi farklı dillerde yakalar / multilingual embeddings |
| Kapak görseli / Cover art | **FLUX.1-dev** | metaforik kapaklar; GPU'da fp8, Mac'te 4-bit / metaphorical covers |

**Ders:** birkaç yıl önce bu iş bulut gerektiriyordu; bugün yerleşik bir ~27–32B model günlük
editoryal işi iyi yapıyor ve bu iş için en büyük modellerle kalite farkı küçük. Donanımın daha
küçükse 8–16 GB bir kart ve 7–8B bir modelle başla — daha yavaş ama çalışır. Modelleri basit bir
şey üzerinden (örn. Ollama) çalıştır ki birini değiştirmek yalnızca bir ayar değişikliği olsun.

_**The lesson:** a few years ago this needed the cloud; today a resident ~27–32B model does the daily
editorial work well, and the quality gap to the biggest models is small for this task. If your
hardware is smaller, start with an 8–16 GB card and a 7–8B model — slower, but it works. Run models
through something simple (e.g. Ollama) so swapping one out is a config change._
