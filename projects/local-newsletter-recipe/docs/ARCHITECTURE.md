# Mimari — parçalar nasıl birleşiyor / Architecture — how the pieces fit

Bu, bir haber üreticisi değil, **insan-önderliğinde bir editoryal boru hattıdır**: yerel bir model
gürültülü bir akışı okunur adaylara indirir, bir insan neyin yayımlanacağına karar verir, sonuç
statik sayfalar ve bir RSS akışı olarak ucuza yayımlanır. Bülten, bu akışın bir çıktısıdır.

_This is not a content generator; it's a **human-led editorial pipeline**: a local model narrows a
noisy stream to readable candidates, a human decides what gets published, and the result ships cheaply
as static pages and an RSS feed. The newsletter is one output of that flow._

## Boru hattı / The pipeline

```text
Kaynaklar (feed'ler, aramalar)   Sources (feeds, searches)
        ↓  topla / collect
Günün havuzu                     The day's pool
        ↓  oku & ele / read & shortlist   (Qwen2.5-32B)
Adaylar                          Candidates
        ↓  taslak yaz / draft             (Qwen3.8-27B: başlık, "neden önemli", kritik)
Taslak sayı                      Draft issue
        ↓  İNSAN / HUMAN                  (seç, düzelt, kaynakla denetle / pick, edit, verify)
Onaylanan sayı                   Approved issue
        ↓  yayınla / publish              (statik HTML + RSS → sunucu / server)
Canlı sayfa + akış               Live page + feed
        ↓  sağlıklı tut / keep healthy    (yedek, ölü link onarımı, "yayınlandı mı?" kontrolü)
```

Her aşama ayrı ve gözlemlenebilir: bir adım bozulursa onu tek başına düzeltir ya da yeniden
çalıştırabilirsin, komşularını yıkmadan.

_Each stage is separate and observable: if one breaks you can fix or re-run it alone, without
toppling its neighbours._

## Tasarım seçimleri / Design choices

**Önce insan / Human first.** Sistem editörün yerini almaz; ona daha iyi adaylar, daha iyi bağlam ve
daha iyi inceleme malzemesi verir. Yayın kararının son mercii her zaman insandır.
_The system doesn't replace the editor; it gives better candidates and better review material. The
human is always the final authority on what publishes._

**Zekâdan önce güvenilirlik / Reliability over raw intelligence.** Amaç her yerde en zeki modeli
kullanmak değil, editoryal güvenilirliktir. Bir işi tutarlı yapan küçük, yerleşik bir model, çok iş
yapıp hepsini tutarsız yapan büyük bir modelden değerlidir.
_The goal isn't the smartest model everywhere; it's editorial reliability. A small resident model that
does one job consistently beats a large one that does many inconsistently._

**Role göre küçük modeller / Small models, by role.** Okuma/eleme, taslak, çeviri, tekilleştirme,
kapak — her rol ayrı değerlendirilebilir ve ayrı değiştirilebilir. Roller kalıcı, modeller
değiştirilebilir (bkz. `MODELS.md`). Bir model yeterince iyiyse birden çok rolü üstlenebilir; bu, tek
GPU'da bellek tasarrufu demektir.
_Reading/shortlisting, drafting, translation, dedup, cover — each role is benchmarked and swapped on
its own. Roles are stable, models are replaceable (see `MODELS.md`). One model may serve several roles
if it's good enough — which saves memory on a single GPU._

**Görünür ve geçersiz kılınabilir kararlar / Visible, overrideable decisions.** Önemli hiçbir şey
sessizce olmamalı. Her öneri açıklanabilir, her model kararı görünür, ve insan her otomatik kararı
geçersiz kılabilir.
_Nothing important happens silently. Every suggestion is explainable, every model decision is visible,
and the human can override any of them._

## Yayınlama — neden statik / Publishing — why static

Çıktı statik HTML + bir RSS akışıdır, bir sunucuya `rsync`'lenir. Veritabanı yok, çalışan uygulama
yok, güvenlik yaması gerektiren bir sunucu tarafı yok — sadece dosyalar. Ucuz, hızlı, taşınması
kolay ve yıllarca ayakta kalır. Dinamik olan tek şey (dil değiştirme, paylaşım) sayfanın içinde,
tarayıcıda çalışır.

_The output is static HTML + an RSS feed, `rsync`'d to a server. No database, no running app, no
server-side to patch — just files. Cheap, fast, portable, and it survives for years. The only dynamic
bits (language toggle, share) run inside the page, in the browser._

> İnsanı araya koyan tasarım `CURATION-APP-DESIGN.md`'de; neyin hangi bölüme girdiği
> `TAXONOMY.md`'de; her şeyin uğruna kurulduğu kurallar `PRINCIPLES.md`'de.
> _The human-in-the-loop design is in `CURATION-APP-DESIGN.md`; how stories are filed is in
> `TAXONOMY.md`; the rules it's all built toward are in `PRINCIPLES.md`._
