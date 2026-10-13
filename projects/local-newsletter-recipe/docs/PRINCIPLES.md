# İlkeler / Principles

Her şeyin üzerine kurulduğu beş kural. Varsayılan değil, seçim — her biri bir bedel taşır, ve her
biri bu işi yapmaya değer kılan şeyin ta kendisi.

_The five rules the whole thing is built toward. They are choices, not defaults — each one costs
something, and each one is the reason the project is worth doing at all._

## 1. Makine taslağı yazar; kararı insan verir / The machine drafts; a human decides

Yerel bir model ağır işi yapar — yüzlerce haberi okumak, elemek, ilk başlığı ve bir "neden önemli"
notunu yazmak. Ama bir okura hiçbir şey, onu bir insan seçmediği sürece ulaşmaz. En değerli iş
insanın işidir: neyin önemli olduğuna karar vermek, ifadeyi düzeltmek, bir iddiayı kaynağıyla
denetlemek. Ayrıca *karar da veren* bir makine bir yayın değildir; bir spam akışıdır.

_A local model does the heavy lifting — reading hundreds of articles, shortlisting, writing a first
headline and a "why it matters". But nothing reaches a reader unless a person chose it. The most
valuable work is the human's: deciding what matters, fixing wording, checking a claim against its
source. A machine that also decides is not a publication; it's a spam feed._

## 2. Tüm yapay zekâ yerelde çalışır / All AI runs locally

Her model, yapanın kendi donanımında çalışır — bulut yapay zekâ servisi yok, API anahtarı yok, haber
başına maliyet yok, ve kaynak malzeme makineden hiç çıkmaz. Birkaç yıl önce bu bulut gerektiriyordu;
bugün yerleşik bir ~27–32B model günlük editoryal işi iyi yapıyor. Yerel-öncelik aynı anda üç şey
demek: gizlilik, bağımsızlık, ve neredeyse sıfır marjinal maliyet.

_Every model runs on the maker's own hardware — no cloud AI service, no API keys, no per-article
cost, and the source material never leaves the machine. A few years ago this needed the cloud; today
a resident ~27–32B model does the daily editorial work well. Local-first is privacy, independence,
and a near-zero marginal cost, all at once._

## 3. Makine konusunda dürüst ol / Honest about the machine

Bir sayfa, bir modelin ne yazdığını ve bir insanın neyi denetlemediğini açıkça söyler. "Bu kritik
yerel bir model tarafından yazıldı ve satır satır denetlenmedi" demek güveni azaltmaz — kazandırır.
Okur, hangi sözlerin makineye ait olduğunu her zaman bilmeli.

_A page says plainly what a model wrote and what a human did not review. "This critique was written by
a local model and is not checked line by line" does not reduce trust — it earns it. The reader should
always know which words are the machine's._

## 4. Herkes için erişilebilir / Accessible to everyone

Anlamlı başlıklar, gerçek alt metin, klavye ve ekran okuyucu desteği, AA kontrast, telefonda okunur.
SEO için değil — çünkü bazılarının okuyamadığı bir yayın bitmemiştir.

_Semantic headings, real alt text, keyboard and screen-reader support, AA contrast, readable on a
phone. Not for SEO — because a publication that some people can't read is not finished._

## 5. Başkalarının emeğine saygı / Respect other people's work

Özgün kaynağa bağlan; başkasının haberini asla kendine barındırma. Görsel sıcak-bağlanır ya da
gömülür ve künyesi verilir, kopyalanmaz. Bu hem bir etik hem de telif hakkının güvenli tarafı.

_Link out to the original; never re-host someone else's article. Media is hotlinked or embedded and
credited, not copied. This is both an ethic and the safe side of copyright._

---

Yukarıdakileri dürüst tutan iki alışkanlık / Two habits that keep the above honest:

- **Kurmadan önce ölç / Measure before building.** İyi görünen birçok fikir ölçülünce çöktü
  (sınıflandırma için küçük modeller, sıralama için benzerlik skorları). Çıkmaz sokakları yaz ki
  bir daha girmeyesin. _Several good-looking ideas collapsed when measured; write down the dead ends._
- **Her sessiz hatayı sesli yap / Make every silent failure loud.** Pahalı hatalar sessiz
  olanlardır — kurulan ama hiç yayımlanmayan bir sayı, fark edilmeden boşalan bir kuyruk. Her birini
  görünür bir uyarıya çevir. _The expensive bugs are the quiet ones — turn each into a visible alert._
