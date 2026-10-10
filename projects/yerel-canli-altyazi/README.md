# Yerel canlı altyazı · Local live captions

> _Generated with Claude (Anthropic) · Bu belge Claude (Anthropic) ile üretildi._

İki dilde konuşulan bir toplantıyı dinler, söyleneni kendi dilinde yazar, karşı dile çevirir
ve canlı altyazı olarak gösterir; toplantı bitince notunu çıkarır. Ses, metin ve notlar
bilgisayardan çıkmaz.

> **Kavram kanıtı (PoC).** Tek bir senaryolu toplantıda denendi: Türkçesi senaryodan okunan
> gerçek bir ses, Almancası yapay bir ses. Gerçek bir toplantıda — kendiliğinden konuşma,
> araya girenler, gürültü, aksan — çalıştığı gösterilmedi. Ölçülenler ve bilinmeyenler: [`DECISIONS.md`](DECISIONS.md).

*Listens to a meeting held in two languages, writes down what is said in its own language,
translates it into the other, and shows both as live captions; writes the notes when the
meeting ends. Audio, text and notes stay on the machine. **A proof of concept:** tested on one
scripted meeting (one real voice reading a script, one synthetic voice), not shown to work
in a real meeting. What was measured
and what is unknown: [`DECISIONS.md`](DECISIONS.md).*

---

## Ne yapar / What it does

- **Dinler / Listens** — bir ses girişini (Loopback, BlackHole, mikrofon) 16 kHz'e çevirir;
  sessizliklerden cümleleri ayırır (silero-vad).
- **Yazar / Transcribes** — her cümleyi kendi dilinde yazar: Whisper large-v3-turbo,
  Apple GPU üzerinde. Dil her cümlede yeniden algılanır.
- **Çevirir / Translates** — önce hızlı bir taslak (NLLB, gri italik), ardından son çeviri
  (yerel 27B dil modeli, beyaz). Gün, saat ve sayılar kodla denetlenir: çeviri bunları
  değiştirirse düzeltilir ya da satır çevrilmeden gösterilir.
- **Gösterir / Shows** — tarayıcıda bir altyazı sayfası; renkli çizgi konuşulan dili gösterir.
- **Not çıkarır / Notes** — toplantı dökümünden Kararlar / Yapılacaklar / Açık Sorular.

## Başlamadan / Before you start

| | |
|---|---|
| **Bilgisayar** | Apple Silicon Mac (M1 ve sonrası). Denendiği makine: M4 Max, 64 GB. Modeller birlikte yaklaşık 22 GB GPU belleği kullanır. |
| **Python** | **3.13** — 3.14 için `torch` / `sentencepiece` paketleri henüz yok. |
| **ffmpeg** | `brew install ffmpeg` |
| **[Ollama](https://ollama.com)** | çeviri ve not modeli için |
| **Ses yönlendirme** | toplantının sesini uygulamaya vermek için: [Loopback](https://rogueamoeba.com/loopback/) (ücretli; denendi) ya da [BlackHole](https://existential.audio/blackhole/) (ücretsiz; denenmedi) |
| **Disk** | yaklaşık 22 GB (modeller bir kez indirilir) |

*Apple Silicon Mac (tested on an M4 Max, 64 GB; the models use about 22 GB of GPU memory together),
Python 3.13, ffmpeg, Ollama, a way to route the meeting's audio to the app — Loopback (paid,
tested) or BlackHole (free, not tested) — and about 22 GB of disk for the models.*

## Kur / Set up

```bash
cd projects/yerel-canli-altyazi
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt
ollama pull batiai/qwen3.8-27b:iq4
```

Whisper ve NLLB ilk çalıştırmada kendiliğinden iner. *Whisper and NLLB download on the first run.*

> Çeviri modeli, Qwen3.8 27B'nin topluluk tarafından hazırlanmış küçültülmüş (IQ4_XS)
> bir sürümü (Apache 2.0). Resmî sürümü tercih edersen: `ollama pull qwen3.8:27b-q4_K_M` ve
> `--model qwen3.8:27b-q4_K_M`. Benim denediğim toplantıda gün ve saat hatası biraz daha fazlaydı.
>
> *The translation model is a smaller (IQ4_XS) version of Qwen3.8 27B prepared by the community (Apache 2.0).
> For the official one: `ollama pull qwen3.8:27b-q4_K_M` and `--model qwen3.8:27b-q4_K_M`;
> on my test meeting it made a few more day and time errors.*

## Çalıştır / Run

**1. Ses geliyor mu? / Is audio arriving?**
```bash
./.venv/bin/python levels.py loopback
```

**2. Canlı altyazı / Live captions** — toplantının iki dilini ver:
```bash
./.venv/bin/python stream.py --live loopback --web --languages tr,de --lines 3 --log toplanti.txt
```
Tarayıcıda `http://127.0.0.1:8770`. Aynı ağdaki başkaları da açabilir; adres terminalde
yazar. *Open the page in a browser; others on the same network can too — the address is
printed in the terminal.*

Gri italik satırlar taslaktır, cümle bitince değişir; beyaz satırlar sondur.
*Grey italic lines are drafts and change when the sentence ends; white lines are final.*

**3. Notlar / Notes** — toplantıdan sonra:
```bash
./.venv/bin/python notes.py toplanti.txt --out notlar.md
```
Notlarda hiç söylenmemiş bir gün ya da sayı varsa terminal uyarır. Göndermeden önce
dökümle karşılaştır. *If the notes contain a day or a number nobody said, the terminal warns.
Check the notes against the transcript before sending them.*

| Seçenek / Option | |
|---|---|
| `--languages tr,de` | toplantının iki dili / the meeting's two languages |
| `--lines 3` | sayfada kaç satır / lines on the page |
| `--record toplanti.wav` | sesi de kaydet (Ctrl-C ile durana kadar) / also keep the audio (until Ctrl-C) |
| `--model ADI` | başka bir Ollama modeli / another Ollama model |
| `--ollama HOST` | Ollama başka bir makinede / Ollama on another machine |
| `--nllb` | son çeviriyi de NLLB yapsın (daha hafif, daha kaba) / NLLB for final lines too (lighter, rougher) |
| `--glossary sozluk.txt` | toplantıya özgü terimler, satır başına `sürüm = Version`; `notes.py` de alır / the meeting's own terms, one `term = Begriff` per line; `notes.py` takes it too |
| `--whisper large-v3` | daha büyük konuşma modeli: bazı Türkçe kelimelerde daha iyi, daha yavaş / the bigger speech model: better on some Turkish words, slower |

## Sınırlar / Limits

- Konuşanı değil, **dili** bilir: iki kişi aynı dili konuşursa ayrılmaz.
  *It knows the language, not the speaker.*
- Whisper bazen yanlış ama geçerli bir Türkçe kelime yazar ve en emin olduğu yerde yanılabilir;
  konuşan kendi sözünü ekranda görür, yanlışsa tekrarlar. *Whisper sometimes writes a real but
  wrong Turkish word, most confidently where it is wrong; speakers see their own words and repeat.*
- Çeviri modeli bazen gün ya da saati değiştirir; kod bunları yakalar ama **yanlış işe
  bağlanmış doğru bir tarihi** yakalayamaz. *A right date attached to the wrong task is not caught.*
- Kayıt ve not alma, ülkeye göre değişen onay kurallarına tabidir.
  *Recording a meeting has consent rules that vary by country.*
- Ölçümler, denemeler ve bilinmeyenler: [`DECISIONS.md`](DECISIONS.md).

## Modeller ve lisansları / Models and licences

| Model | Görev / Role | Lisans / Licence |
|---|---|---|
| Whisper large-v3-turbo (MLX) | konuşmayı yazıya / speech to text | MIT |
| Whisper large-v3 (MLX), isteğe bağlı / optional | konuşmayı yazıya / speech to text | MIT |
| NLLB-200 distilled 600M | taslak çeviri / draft translation | CC-BY-NC 4.0 (ticari olmayan / non-commercial) |
| Qwen3.8 27B | son çeviri ve notlar / final translation and notes | Apache 2.0 |
| silero-vad | konuşma algılama / speech detection | MIT |
