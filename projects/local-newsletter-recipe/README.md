# Yerel haber bülteni tarifi · Local newsletter recipe

> _Generated with Claude Opus 4.8 (Anthropic) · Bu belge Claude Opus 4.8 ile üretildi._

> ⚠ **Sürekli değişiyor / Work in progress.** [demle.me](https://demle.me)'nin nasıl yapıldığının
> bir anlık görüntüsü — bitmiş bir ürün değil. Bir tarif, şablon değil.
> _A snapshot of how demle.me is made, not a finished product. A blueprint, not a spec._

Bu, "tek tıkla demle.me" kurulumu **değil**. Paylaştığım şey **yöntem**: promptlar, içerik
taksonomisi, kaynak listesi ve her parçayı senin kurulumuna göre kurduran **builder prompt**'lar —
kendi küçük, yerel bülteninı kurabilesin diye.

*This is not a one-click clone of demle.me. It's the **method** — the prompts, the content
taxonomy, the source list, and **builder prompts** you paste into your own AI — so you can build
your own small, local-first publication, shaped around your topic, language and hardware.*

---

## Fikir / The idea

Yerel bir yapay zekâ yüzlerce kaynağı okuyup taslak yazar; **okura ulaşan her kararı insan verir**;
sonuç açıkça ve ucuza yayımlanır. Bulut yapay zekâ yok, haber başına maliyet yok, kara kutu yok.

*Local AI reads a flood of sources and drafts; a human makes every choice that reaches a reader;
the result is published openly and cheaply. No cloud AI, no per-article cost, no black box.*

## Kendi bültenini kur — altı adım / Build your own — six steps

Komut değil, **karar**. Her adım, burada ödünç alabileceğin bir malzemeye ve kendi yapay zekâna
yapıştırıp o parçayı kurdurabileceğin bir **builder prompt**'a işaret eder.
*Decisions, not commands. Each step points to material you can borrow and a builder prompt.*

1. **Sahip olduğun bir motor seç / Pick an engine you own** — bilgisayarında çalışan bir model. → `docs/MODELS.md`
2. **Kaynaklarını ver / Point it at your sources** — feed'ler, aramalar. → `recipe/` · kur → `builders/collector.md`
3. **Model okusun, elesin, taslak yazsın / Let it read, shortlist, draft** → `prompts/` · `docs/TAXONOMY.md` · kur → `builders/drafting.md`
4. **Araya insanı koy / Put a human in the loop** — asla otomatik yayın. → `docs/CURATION-APP-DESIGN.md` · kur → `builders/curation-app.md`
5. **Basitçe yayınla / Publish simply** — statik sayfa + RSS. → `docs/ARCHITECTURE.md` · kur → `builders/publisher.md`
6. **Sağlıklı tut / Keep it healthy** — yedek, ölü link onarımı, "yayınlandı mı?" kontrolü. → kur → `builders/upkeep.md`

## Yapay zekâna kurdur / Have your AI build it

Her parça için `builders/` içinde bir prompt var. Birini bir yapay zekâ asistanına yapıştır; sana
birkaç soru sorup **senin** sürümünü üretir — zor kazanılmış kurallar promptun içinde gömülü.
Sırayla kur: collector → drafting → curation → publisher → upkeep. Çıkan şey başlangıç iskeleti,
bitmiş demle.me değil.
*Paste a builder prompt into an AI assistant; it asks a few questions, then generates your version
with the hard-won rules baked in. A starting skeleton you then shape.*

## Işık ile imza! / A signature in the light

demle.me’de üretilen bültenlerin kapakları ismimin *“Tansel”* anlamını bir imza gibi taşır —
sabahın ilk ışıkları (`prompts/03-cover.md`). Sen de kendininkini verebilirsin?
*On demle.me, the newsletter covers carry the meaning of my name, Tansel, like a signature — the
first light of morning. You can give yours your own.*

## Bu depoda ne var / What's in this repo

- **`builders/`** — her parça için bir prompt; yapay zekâna yapıştır, kendi sürümünü kursun.
- **`prompts/`** — modellerin çalıştırdığı gerçek promptlar (başlık, kritik, çeviri, kapak).
- **`docs/`** — mimari, ilkeler, içerik taksonomisi (ölçümleri ve çıkmaz sokaklarıyla),
  kürasyon uygulaması tasarım notları, boru hattı tasarımı.
- **`recipe/`** — kaynak listesi ve konu/sözlük ayarları, başlangıç örneği olarak.

Burada **olmayan**: çalışır haldeki tam boru hattı ve sunucularıma bağlı hiçbir şey.
*Not here: the full runnable pipeline, and anything tied to my own servers.*

## İlkeler / Principles

- Makine taslağı yazar, **kararı insan verir** / the machine drafts, a human decides.
- Tüm yapay zekâ **yerelde** çalışır / all AI runs locally — private, no cloud, no cost per article.
- **Dürüstlük** / honest about what the machine wrote and what wasn't reviewed.
- **Erişilebilirlik** / built to be accessible to everyone.
- Başkalarının emeğine saygı / links out and credits others, never re-hosts their work.

Bu yöntem bir yapay zekâ kodlama ortağıyla (**Claude**) kuruldu; haberleri kendi makinemdeki açık
modeller yazıyor — farklı bir yapay zekâ, farklı bir iş. Her editoryal seçim insanın.

## Lisans ve künye / License & credit

- Kod / code: **MIT** (`LICENSE`). Promptlar, belgeler, tarif / prompts, docs, recipe:
  **CC-BY-4.0** (`LICENSE-DOCS.md`).
- Üstüne bir şey kurarsan lütfen künye düş / if you build on this, please credit:
  **Tansel Okay ([demle.me](https://demle.me)), yapay zekâ kodlama ortağı Claude ile kuruldu.**
