# İçerik taksonomisi — üç bölüm, yedi etiket / Content taxonomy — three sections, seven tags

Bir örnek olarak paylaşıyorum: benim günlük AI bültenimin tüm arşivi üzerinde — **74 sayıda 904
yayımlanmış haber** — ölçülüp oturtuldu. Kendi konuna uyarlaman için bir başlangıç, bir reçete değil.

_Shared as an example: settled and measured on my daily AI newsletter's whole archive — **904 published
articles across 74 issues**. A starting point to adapt to your own topic, not a prescription._

---

## Eski "sütunlar" neden gitmek zorundaydı / Why the old "pillars" had to go

Bir öğenin sütunu, **toplandığı** gruptu — yani öznesini değil, nereden geldiğini kaydediyordu.
Arşivde ölçülen sonuçlar:

_An item's pillar was the group it was collected from — so it recorded provenance, never subject.
Measured across the archive:_

| sütun / pillar | öğe / items | gerçekte ne tutuyordu / what it actually held |
|---|---|---|
| mizah / humor | 85 | **80'i iki teknoloji kaynağından** — nükleer yakıt, hibrit uçak, süper-zekâ yasağı. Bir sınıflandırıcı etiketi **%2** onayladı. / 80 from two tech sources; a classifier agreed 2% of the time. |
| küresel / global | 298 | her şeyin %33'ü, **kaynak ülkeye** göre tanımlı, konuya göre değil / 33% of everything, by source country, not subject |
| açıklayıcı / explainer | 65 | 54'ü tek bir blog yazarından / 54 from one blogger |
| kariyer / career | 3 | 74 sayıda / in 74 issues |

Asıl kusur: **eski şema üç ekseni karıştırıyordu.** Bazı sütunlar içerik, biri (küresel) köken, biri
(çoklu-ortam) biçim hakkındaydı. Bir haber aynı anda üçü de olabilir; tek cevaba zorlamak yanlışları
garanti eder — üstelik köken ve biçim, feed'den ve URL'den zaten bedava biliniyor, hiçbir modele
sorulmamalı.

_The deeper fault: the old scheme mixed three axes — some pillars were about content, one (global) about
origin, one (multimedia) about format. A story can be all three, so forcing one answer guarantees wrong
ones — and origin and format are already free from the feed and URL, so no model should guess them._

---

## Üç bölüm / The three sections

Her biri okurun gerçekten sorduğu bir soruyu yanıtlar. Paylar, 904 haberlik arşivin ölçülen dağılımı.

_Each answers a question the reader is actually asking. Shares are the measured split of the archive._

| bölüm / section | soru / the question | tutar / holds | pay / share |
|---|---|---|---|
| **Ne oldu?** / What happened | ne oldu | `models`, `donanim` | 33% |
| **Ne işe yarıyor?** / What's it for | ne işe yarıyor | `uygulama`, `bilim` | 32% |
| **Ne düşünmeli?** / What to make of it | ne düşünmeli | `kuram`, `politika`, `olaylar` | 35% |

Belirleyici etken doğruluk değil, **denge**ydi. Dört gruplama denendi, hepsi el-etiketlerine karşı
**%85–87** aldı — 60 haberde bu tek-haberlik fark, yani gürültü. Diğerleri bültenin %45–52'sini tek
bir bölüme yığıyordu (küresel-%33 sorununun başka adı). Tek dengeli bölünme bu.

_The deciding factor was **balance**, not accuracy. Four groupings all scored 85–87% against hand
labels — on 60 articles that's noise. The alternatives put 45–52% of the newsletter in one section
(the global-at-33% problem relabelled). This is the only even split._

**Bölüm sayısını okur için seç. Model kayıtsızdır.** _Choose the section count for the reader; the
model is indifferent._

---

## Yedi etiket / The seven tags

Bölüm türetilir; **etiket** modelin atadığı ve okurun süzdüğü şeydir.

_The section is derived; the **tag** is what the model assigns and the reader filters on._

- **`models`** — Adı geçen bir model/sistem ya da onu yapan kuruluş: sürümler, yetenekler,
  kıyaslamalar, yatırım, satın almalar, lab stratejisi. _A named model/system or the org building it._
- **`kuram`** — Yapay zekânın **nasıl çalıştığı**. Yöntemler, mimariler, eğitim, yorumlanabilirlik,
  sınırlar, bir bilim olarak değerlendirme. _How AI works: methods, architectures, training, limits._
- **`bilim`** — **Dünya** hakkında öğrenilen şey, **araç olarak yapay zekâyla**. Keşif başka bir alana
  ait, yapay zekâ ona ulaşan alettir. _What we learned about the world, with AI as the instrument._
- **`uygulama`** — Bir **iş alanında** değişen şey — tıp, inşaat, tarım, hukuk, eğitim, medya, üretim.
  Haber, bir **sektörün** değişmesidir. _What changed in a field of work; the news is a sector changed._
- **`donanim`** — Yapay zekânın **üzerinde çalıştığı** şey: çipler, hızlandırıcılar, veri merkezleri,
  bellek, fab'lar, güç ve soğutma. _What AI runs on: chips, data centres, memory, power, cooling._
- **`politika`** — **Kuralları kim koyar**: düzenleme, hukuk, mahkemeler, ihracat denetimi, ulusal
  strateji, standartlar, jeopolitik. _Who sets the rules: regulation, courts, standards, geopolitics._
- **`olaylar`** — **Ne ters gitti**: arızalar, kötüye kullanım, önyargı, deepfake, dolandırıcılık,
  ihlaller, zararlar, bunlara dair davalar. _What went wrong: failures, misuse, bias, deepfakes, harms._

### Sınır testleri / Boundary tests

Yedi yönlü bir seçim bunlar olmadan karara bağlanamaz. Her biri bir cevabı olan bir sorudur, bir
his değil. _A 7-way choice is undecidable without these — each is a question with an answer, not a vibe._

- Bir alanda iş yapan model → haber **alanın** değişmesiyse `uygulama`, **yeteneğin** varlığıysa
  `models`. _Field changed → uygulama; capability exists → models._
- Bir lab'ın duyurduğu çip → `donanim`. Haber çip, lab değil. _A chip a lab announced → donanim._
- Yapay zekâyla varılan bilimsel sonuç → `bilim`. Yapay zekânın kendisi hakkında sonuç → `kuram`.
- Deepfake dolandırıcılığı → `olaylar`. Deepfake hakkında yasa → `politika`.
- Bir zarara dava → `olaylar`. Kural koyan düzenleme/karar → `politika`.
- Bir yazılım çerçevesi/kütüphane sürümü → ne **için**se o; **asla** `donanim` değil.

### Etiket değil, üst-veri — ve asla bir bölüm / Metadata, not tags — and never a section

Feed'den ve URL'den belirlenir, bedava ve tam doğru: _Determined from the feed and URL, free and exact:_

- **köken / origin** — kaynağın ülkesi/dili. Eskiden `global`'di; bir sınıflandırıcı onu **%28**
  onaylıyordu, çünkü köken bir içerik sorusu değil. _Was `global`; a classifier agreed 28% of the time._
- **biçim / format** — video ya da podcast. Eskiden `multimedia`'ydı; onay **%18**, aynı sebeple.
  _Was `multimedia`; agreement 18%._

İkisi de süzgeç olarak yararlı. Hiçbiri bir bölüm değil, hiçbiri bir modele sorulmamalı.
_Both are useful filters. Neither is a section, and neither should be asked of a model._

---

## Bölümü türetmek / Deriving the section

İlk eşleşen kazanır. Sıra editoryal önceliği kodlar: bir zarar, çiğnediği kuralı geçer; o da üzerinde
çalıştığı donanımı geçer. _First match wins; the order encodes editorial priority._

```text
olaylar   -> Ne düşünmeli?        politika  -> Ne düşünmeli?
donanim   -> Ne oldu?             bilim     -> Ne işe yarıyor?
models    -> Ne oldu?             uygulama  -> Ne işe yarıyor?
kuram     -> Ne düşünmeli?
```

Bölüm türetilmiş olduğu için, bölümler sonradan yeniden kesilebilir — birleştirilebilir, bölünebilir,
yeniden adlandırılabilir — **tek bir haberi bile yeniden sınıflandırmadan.**

_Because the section is derived, the sections can be re-cut later — merged, split, renamed — without
reclassifying a single article._

---

## Ne ölçüldü / What was measured

| soru / question | cevap / answer | nasıl / how |
|---|---|---|
| Yerel bir model içeriğe göre sınıflar mı? / Can a local model file by content? | **evet, %83 / yes, 83%** | 27B, 60 kör el-etiketine karşı |
| En zayıf sınır? / Weakest boundary? | `bilim` **%57** | aynı örnek |
| Sağlam olanlar? / The solid ones? | `donanim`, `politika` **%100** | aynı örnek |
| 3, 7'yi geçer mi? / Does 3 beat 7? | hayır — %85 vs %83 | iki etiket kümesini de daraltarak |
| 9B yeter mi? / Would a 9B do? | **hayır / no** | `models`'te %56; ürün lansmanını iş-yeri haberi okur |
| Gömmeler yeter mi? / Embeddings? | **hayır — %66 / no** | bge-m3 + k-NN, 5 kat |
| Optimize etmeye değer mi? / Worth optimising? | **hayır / no** | 904 haber 231 sn → haftalık sayı başına ~23 sn |

### Gömmeler neden tam olarak başarısız / Why embeddings fail, specifically

Konuya göre kümelerler; bu bölümler **role** göre tanımlı. Bir çip hakkında üç haber `donanim` (yeni
hızlandırıcı), `models` (onu duyuran lab) ya da `politika` (ihracat denetimi) olabilir — neredeyse aynı
kelimeler, üç bölüm. "Bu ne tür bir olay" ile tanımlı iki etiket en kötü çöker: `olaylar` %46, `bilim`
%47. Gömmeler iyi oldukları işte kalır: diller-arası tekilleştirme, ilgili-haber bağlantıları, "bunu
daha önce işledik mi".

_They cluster by **topic**; these sections are defined by **role**. Three chip stories can be donanim,
models or politika — near-identical vocabulary, three sections. Embeddings stay useful for what they're
good at: cross-language dedup, related-article links, "have we covered this before"._

### Neden 27B ve daha küçüğü değil / Why the 27B and nothing smaller

Üretim için zaten bellekte, bu yüzden sınıflandırma **model takası** gerektirmez — sabahları kırılgan
yapan şey tam da budur. Haftalık sayı başına ~23 sn'de çözülecek bir hesap sorunu yok; daha küçük bir
model, kimsenin fark edemeyeceği bir tasarruf için gerçek doğruluk feda eder.

_It's already resident for generation, so classification costs no model swap — the thing that makes
mornings fragile. At ~23 s per weekly issue there's no compute problem, and a smaller model trades real
accuracy for a saving nobody can perceive._

---

## Açık uçlar / Open questions

1. **`bilim` tek zayıf sınır (%57).** Üç şeyle çakışıyor: araç-olarak-yapay-zekâ sonuçları (doğru),
   yapay zekâsız saf bilim (bültende hiç olmamalı — bir feed sorunu) ve tartışmalı biçimde `kuram` olan
   yöntem makaleleri. Öneri: **kesinlikle "yapay zekâ alettir"** diye tanımla, yapay-zekâsız bilim
   toplama aşamasında düşsün. _Define it strictly as "AI was the instrument"; let non-AI science fall
   out at collection._
2. **Ekonomi ve öngörü haberleri** — "AI 2030'da GSYİH'yi %32 artırabilir" yedisinin hiçbirine temiz
   oturmuyor; şimdilik `kuram`'a düşüyor. Bir yuva ya da kural gerek. _Economic/forecast stories fit none
   cleanly; they need a home or a rule._
3. **Hafif/eğlenceli bir bölümün yeri var mı?** Haftada ~60 pop-bilim öğesi bu şemada
   `uygulama`/`bilim`'e dağılıyor. Doğru olabilir — ya da hafif bölümü kazara değil, bilerek tutmaya
   değer. _Is a light section worth keeping deliberately rather than by accident?_
