# Kürasyon uygulaması — tasarım / Curation app — design

İnsanı araya koyan parça budur: günün adaylarını otomatik yazılmış taslaklarıyla gösteren, onları
düzeltip hangilerinin gireceğini seçtiğin ve tek tuşla yayımladığın **küçük, yerel bir web
uygulaması**. Yönlendirici ilke: **otomasyon taslağı yazar, sen onaylarsın, sonra yayımlanır.** Model
çıktısı bir *taslaktır*, asla görülmeden yayımlanmaz — uydurma ayrıntı riskinin (makul görünen ama
yanlış bir ayrıntı) tek gerçek cevabı budur.

_This is the human-in-the-loop piece: a small **local web app** that shows the day's candidates with
their auto-drafted titles/blurbs, lets you edit them, choose which go in, and **publish** in one click.
Guiding principle: **automation drafts, you approve, then it ships.** The model output is a draft,
never published unseen — the only real answer to hallucination risk (a plausible but false specific)._

## Neden yerel / Why local

- Kendi makinende (localhost) çalışır — yeni dış barındırma yok, kimlik doğrulama derdi yok.
- Mevcut boru hattını yeniden kullanır: taslak için üretim adımı, render için hafif şablon, yayın
  için var olan dağıtım betiği.

_Runs on your own machine (localhost) — no new external hosting, no auth headaches. Reuses the existing
pipeline: the draft step for drafts, the light template for rendering, the deploy step to ship._

## Yığın — minimal, derleme adımı yok / Stack — minimal, no build step

- **Arka uç / Backend:** mevcut sanal ortamda bir FastAPI, localhost'ta uvicorn ile. _FastAPI in your
  venv, served by uvicorn on localhost._
- **Ön yüz / Frontend:** tek bir statik HTML sayfası + sade JS — React/derleme yok. Bültenin açık
  temasıyla biçimlendirilir ki editör *çıktının göründüğü gibi* görsün. _A single static HTML page +
  vanilla JS, styled with the newsletter theme so the editor looks like the output._
- **Depolama / Storage:** basit dosyalar — tarih başına bir JSON (taslaklar + düzeltmelerin + dahil
  et/sıra durumu). Veritabanı yok. _Plain files — one JSON per date. No database._

## Akış / Data flow

1. **Taslakları hazırla / Prepare drafts** (günde bir ya da istek üzerine bir düğme): günün adaylarını
   topla, her biri için içerikten sapmayan bir başlık + "neden önemli" üret, görselleri getir, JSON'a
   önbellekle. _Pull the day's candidates, draft a faithful title + "why it matters" for each, cache._
2. **Küre / Curate** (tarayıcı): taslağı aç; başlık/metni yerinde düzelt, dahil et/çıkar, yeniden
   sırala, istersen bölümünü değiştir. _Open the draft; edit title/blurb inline, toggle include, reorder._
3. **Yayınla / Publish:** kürelenmiş öğeleri şablona render et → dağıt → düzenlediğin her çifti
   ileride ince-ayar için sakla. _Render the curated items → deploy → keep every edited pair for later
   fine-tuning._

## Ekranlar / Screens

- **Sayı editörü / Issue editor:** başlık çubuğu (tarih, öğe sayısı, Hazırla / Önizle / Yayınla
  düğmeleri). Her aday düzenlenebilir bir kart: görsel, kaynak bağlantısı, skor, **kaynak rozeti**
  (hangi toplama kanalından geldiği), düzenlenebilir başlık ve metin, dahil-et kutusu, sürükleme
  tutamacı. _Each candidate is an editable card: image, source link, score, source badge, editable
  title & blurb, include checkbox, drag handle._
- **Önizleme / Preview:** gerçek bülten HTML'i bir iframe içinde. _The real newsletter HTML in an iframe._

## Baştan gömülü kurallar / Rules baked in from the start

- **Asla otomatik yayın / Never auto-publish.** Yayın her zaman bir insan tıklamasıyla olur.
- **Alan bırakınca kaydet / Save per edit.** Her düzeltme anında diske yazılır; bir kaza bir saatlik
  kürasyonu silmesin. _Every edit is written to disk immediately._
- **Kaynakları birleştir, URL'ye göre tekilleştir / Pool sources, dedupe by URL.** Birden çok toplama
  kanalı tek bir kürelenmiş sayıda buluşur, her biri bir kaynak rozetiyle; aynı haber iki kanalda da
  varsa bir kez görünür. _Multiple collection tracks meet in one issue, each with a source badge;
  dedupe by final URL._
- **İstek üzerine hazırla / Prepare on demand.** Ağır üretim adımı sabah boru hattına maliyet eklemez;
  uygulamayı açınca bir düğmeyle çalışır. _The heavy draft step runs on a button, not in the morning job._
- **Yerel ağdan eriş / Reach over the LAN.** Mac'ten ya da telefondan aç (ev ağı, herkese açık değil);
  başka cihazlar erişebildiği için URL'ye basit bir paylaşılan-gizli anahtar ekle. _Open from the Mac
  or your phone on the home LAN; add a simple shared-secret token since other devices can reach it._
- **Düzeltmeleri yakıt olarak sakla / Capture edits as fuel.** Metnini değiştirdiğin her öğe için
  taslak-vs-son çiftini bir JSONL'ye ekle — ileride kendi küçük çeviri/başlık modelini eğitmek için.
  _For each item you edited, append the draft-vs-final pair to a JSONL — to fine-tune your own small
  model later._
