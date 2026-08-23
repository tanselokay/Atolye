# Yerel anlamsal arama · Local semantic search

> _Generated with Claude Opus 4.8 (Anthropic) · Bu belge Claude Opus 4.8 ile üretildi._

Belgelerini **anlamıyla** bul — yerel ve özel. `.docx`, `.pptx`, `.xmind` dosyalarını
bilgisayarında dizinler; Türkçe doğal cümleyle ararsın, hiçbir şey buluttan geçmez.

> **Kavram kanıtı (PoC).** Çalışır, ama geniş kullanımda test edilmedi. İçerikler birbirinden
> farklıysa iyi sonuç verir; birbirine çok benzeyen dosyalarda anlam tek başına yetmez, tarih/
> üstveri filtresi devreye girer.

*A proof of concept: find your Word/PowerPoint/XMind files by **meaning**, fully local and private.
Turkish-first. Works well when documents differ in content; leans on the date/metadata filter for
near-identical files.*

---

## Ne yapar / What it does
- **Çıkar / Extract** — `.docx` (bölüm + tablo), `.pptx` (slayt + notlar), `.xmind` (zihin haritası)
  metnini ve üstveriyi (oluşturma tarihi, yazar, başlık) okur.
- **Konumlandır / Embed** — metnin anlamını çok boyutlu bir uzayda konumlandırır (**bge-m3**).
- **İndeksle / Index** — vektör + tam metin (SQLite FTS5) + tarih, tek bir yerel SQLite dosyasında.
- **Ara / Search** — anlamsal ⊕ anahtar sözcük ⊕ tarih; RRF ile birleşir, **anlam öncelikli**.
  Türkçe göreli zaman ifadelerini anlar: *geçen hafta, dün, geçen ay, ağustos…*

## Başlamadan / Before you start
Hiçbir ön bilgi varsaymıyoruz. Sırayla:
- **Python 3.9+** — yoksa [python.org](https://www.python.org/downloads/)'dan kur.
  Doğrula: `python3 --version` (Windows: `py --version`).
- **[Ollama](https://ollama.com)** — kur, sonra modeli indir (bir kez, ~1,2 GB):
  ```
  ollama pull bge-m3
  ```
- **Git** — *isteğe bağlı.* Kodu Git ile **veya** ZIP indirerek alabilirsin (aşağıda).
- Ayrıca: bir **terminal** (Terminal / PowerShell / Komut İstemi), **internet** ve ~**2 GB boş disk**.
- Python paketleri (python-docx, python-pptx) bir sonraki adımda kurulur.

*No prior knowledge assumed. You need Python 3.9+ ([python.org](https://www.python.org/downloads/)),
Ollama ([ollama.com](https://ollama.com)) with `ollama pull bge-m3`, a terminal, internet, and ~2 GB
free disk. **Git is optional** — get the code with Git or a ZIP (below).*

> Ollama başka bir makinedeyse, adresini `ATOLYE_OLLAMA` ile ver (varsayılan
> `http://localhost:11434`). Vektör modelini `ATOLYE_EMBED` ile değiştirebilirsin (varsayılan `bge-m3`).

---

## Kodu al / Get the code
Sadece bu projeyi al (tüm depoyu değil). İki yol:

**Git yoksa (en kolay):** ZIP'i doğrudan indir →
**[yerel-anlamsal-arama.zip](https://github.com/tanselokay/Atolye/releases/download/v0.1/yerel-anlamsal-arama.zip)**
→ aç → klasöre gir. (Git, GitHub hesabı, komut gerekmez.)

**Git varsa:**
```bash
git clone --filter=blob:none --sparse https://github.com/tanselokay/Atolye.git
git -C Atolye sparse-checkout set projects/yerel-anlamsal-arama
cd Atolye/projects/yerel-anlamsal-arama
```

*No Git needed: download **[yerel-anlamsal-arama.zip](https://github.com/tanselokay/Atolye/releases/download/v0.1/yerel-anlamsal-arama.zip)**
directly, unzip, and open the folder. With Git: the sparse-checkout above fetches only this project.*

## Kurulum / Setup

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ollama yerel değilse / if Ollama is on another host:

```bash
# macOS / Linux
export ATOLYE_OLLAMA=http://192.168.1.50:11434
```
```powershell
# Windows (PowerShell)
$env:ATOLYE_OLLAMA = "http://192.168.1.50:11434"
```

---

## Çalıştır / Run

**1) (İsteğe bağlı) örnek belgeler üret / build a sample corpus**
```bash
python sample/make_sample.py     # karışık Türkçe .docx/.pptx (yakın kopyalar + aynı adlı notlar)
python sample/make_xmind.py      # örnek .xmind zihin haritaları
```

**2) Bir dizini indeksle / index a folder**
```bash
# macOS / Linux
python index.py ./sample atolye_finder.db
```
```powershell
# Windows
python index.py .\sample atolye_finder.db
```

**3) Ara / search**
```bash
python search.py "geçen ay proje raporu" atolye_finder.db
python search.py "gecikmiş ödeme uyarısı" atolye_finder.db
```

**4) (İsteğe bağlı) doğrula / validate** — yalnızca toplam skoru yazar, dosya içeriği sızmaz:
```bash
python validate.py atolye_finder.db queries.example.json
```

> Not: macOS/Linux'ta `python3`, Windows'ta `python` ya da `py` kullanman gerekebilir.
> İndeks dosyası (`*.db`) belgelerinin metnini içerir — yerelde kalır, paylaşma.

---

## Nasıl çalışır / How it works
İki parça bir arada: **anlam** (bge-m3 ile anlam benzerliği) ve **anahtar sözcük + üstveri**
(FTS5 + tarih/yazar/tür, Elasticsearch benzeri). Biri anlamı bulur, diğeri kesin terimi ve
kontrolü sağlar; sonra birleşir. Okuma sırası ve ayrıntılar için sayının hikâyesine bak (demle.me).

### Zaman ifadeleri / Time phrases
"geçen hafta", "dün", "geçen ay", "ağustos", "son 3 gün" gibi ifadeler `timeparse.py` içinde
**basit kurallarla** bir tarih aralığına çevrilir (hafta Pazartesi başlar; "geçen hafta" = önceki
tam Pazartesi–Pazar). Bu aralık, dosyanın **oluşturma/değiştirme** tarihine göre bir **süzgeç**
olarak uygulanır; model bu ifadeyi görmez — ifade sorgudan çıkarılır, kalanı anlamsal aramaya gider.
Sınırlar: liste **sabittir** (tanınmayan ifade, süzgeç uygulanmadan geçer); belgede tarih yoksa
dosya sisteminin tarihine düşülür (kopyalanmış dosyada yanıltıcı olabilir).

*Relative-time phrases are parsed to a date range by simple rules in `timeparse.py` (week starts
Monday; "last week" = the previous full Mon–Sun), then applied as a filter on each file's
created/modified date. The model never sees the phrase — it's stripped from the query. Limits: the
phrase list is fixed (an unrecognized phrase applies no filter); if a document has no embedded date,
the filesystem date is used, which a copied file can make misleading.*

## Sınırlar / Limits
- Küçük örneklemde ölçüldü; yön sağlam, kesin rakamlar küçük örneklem.
- Yalnızca metin katmanı olan dosyalar — **taranmış/görsel belgeler için OCR yok**.
- Anahtar sözcük eşleşmesi yalnızca kesin terimlerde (kod, tarih, tırnakla) devreye girer;
  doğal cümlelerde anlam önceliklidir.

## Bunu nasıl büyütebilirsin / How you could grow it
Bu bir kavram kanıtı. Kullanmayı düşünüyorsan, aynı fikri kendi ihtiyacına göre şu yönlerde
genişletebilirsin:
- **Ölçek için vektör indeksi (ANN).** Belge sayısı artınca kaba tarama yerine hızlı yaklaşık
  indeks (ör. `sqlite-vec`, FAISS, hnswlib) — on binlerce belgede hızlı kalır.
- **Kalıcı web arayüzü.** Klasörü yeniden aramak ve yeni belgeleri indekse eklemek için yerel bir
  sayfa — her seferinde komut çalıştırmadan.
- **Daha güçlü yerel model / sunucu.** Daha iyi ya da çok dilli bir gömme modeli; ekip için
  paylaşılan tek bir yerel AI sunucusu.
- **Üstveri çıkarım genişleticisi.** Belgeye özel alanlar (müşteri, proje kodu, tutar, sözleşme
  tarihi…) çıkarıp aranabilir ve süzülebilir kıl.
- **Erişim denetimi.** Kullanıcının yetkisi olmayan belgeleri sonuç listesinden ele (ekip/kurumsal
  kullanım için).
- **Artımlı güncelleme.** Değişen ya da yeni eklenen dosyaları otomatik yeniden indeksle (izleme).

## Güncelleme ve ayarlama / Updating & customizing
- **Güncelle:** `git pull` (ZIP indirdiysen yeni ZIP'i indir). Verilerin — belgelerin, `*.db`,
  indirilen model — depo dışında; güncelleme onlara dokunmaz.
- **Ayarla, kodu değiştirme:** farklı bir Ollama adresi veya model için ortam değişkeni ver
  (`ATOLYE_OLLAMA`, `ATOLYE_EMBED`). İzlenen dosyaları düzenlemezsin, `git pull` temiz kalır.
- **Kodu değiştireceksen:** fork'la ya da bir dalda çalış; yoksa `git pull` çakışabilir.

*Update with `git pull` (your data lives outside the repo, untouched). Configure via the
`ATOLYE_OLLAMA` / `ATOLYE_EMBED` environment variables instead of editing tracked files, so pulls
stay clean. If you do edit the code, fork or use a branch to avoid merge conflicts.*

## Lisans / License
MIT — bkz. deponun kökündeki `LICENSE`.
