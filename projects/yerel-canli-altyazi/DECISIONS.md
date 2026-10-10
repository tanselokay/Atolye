# Ne ölçtüm, neyi bilmiyorum · What I measured, and what I do not know

> _Generated with Claude (Anthropic) · Bu belge Claude (Anthropic) ile üretildi._

Türkçe aşağıda. · *For English, see [English](#english).*

## Türkçe

> **Bu bir kavram kanıtıdır, bir ürün değil.** Aşağıdaki her şey, tek bir senaryolu toplantıda ölçüldü. Bu toplantıda bir gerçek ses ve bir yapay ses, metni bir senaryodan okudu. Daha önceki denemelerde yalnızca yapay sesler kullanıldı. Bu, parçaların bir araya getirilebildiğini ve tek bir bilgisayarda çalıştırılabildiğini gösteriyor. Gerçek bir toplantıda canlı altyazıların veya toplantı notlarının işe yaradığını göstermiyor; demoda görülen kurulum dahil. Rakamları laboratuvar notları olarak oku.

### Ne denendi

Tek bir proje değerlendirme toplantısını denedim. Toplantıda 18 kısa söz sırası vardı; biri Türkçe, diğeri Almanca konuşuyordu. Her iki bölüm de önceden yazılmıştı. Tanıtım videosunda Türkçe ses benim, metinden okuyup evde tek bir mikrofonla kaydettim. Almanca ses ise yapay bir sestir; Piper adlı, yazıyı sese dönüştüren bir programla üretildi. Kullanılan ses `de_DE-thorsten-high` idi, CC0 lisansıyla ücretsizdir. Aşağıdaki laboratuvar notlarındaki ölçümler daha önce yapıldı ve yalnızca yapay sesler kullanıldı. Bunların çoğu için Speechelo'yu, üç dilli test için ise macOS'un yerleşik seslerini kullandım. Ses, bir uygulamadan diğerine ses aktaran Loopback adlı program üzerinden, 64 GB bellekli bir M4 Max MacBook Pro'da canlı olarak alındı.

Bu, olabilecek en kolay durumdur. Koşullar çok kontrollüydü:

- **Temiz duraklar**: Metin, söz sıraları arasındaki durakları belirlediği için her cümle tam bittiği yerde kesildi.
- **Üst üste konuşma yok**: Kimse "ehm" demedi, baştan başlamadı ya da başkasının sözünü kesmedi.
- **Dil başına tek ses**: Aksan yoktu. Türkçe ses, bir odada tek mikrofonla kaydedildi; Almanca ses ise yapaydı.
- **Üç saniyelik duraklar**: Çevirinin yanıt gelmeden ekranda görünmesi için söz sıraları arasına bu durakları koydum.
- **Kısa cümleler**: Hiçbiri, 6 saniyelik zorunlu kesmeye takılacak kadar uzun değildi.
- **İsim ya da jargon yok**: Tek teknik terim "release notes" idi.

Gerçek konuşmalarda bunların hepsi bozulur; her biri, konuşmayı yazıya dökmenin bilinen bir hata kaynağıdır ve hiçbiri burada denenmedi. 9 Eylül'de bir podcast üzerinde gayri resmi bir deneme yaptım, İngilizceyi Türkçeye çevirdim. Ekranda hata vermeden çalıştı, ama ölçüm yapmadım.

### Videoda ne var

Video, Apple GPU üzerinde çalışan dört adımı gösteriyor. Önce Whisper large-v3-turbo, konuşmayı yazıya döken açık bir modelin hızlı sürümü, sesi metne çeviriyor ve 2,5 GB bellek kullanıyor. Ardından NLLB-200 600M, Meta'nın çeviri modeli, her satır için hızlı bir taslak sunuyor. Sonra qwen3.8 27B, burada sıkıştırılmış bir sürümde büyük bir dil modeli, nihai çeviriyi ve notları yazıyor; bu adım 16,5 GB bellek gerektiriyor. Toplamda bu kurulum yaklaşık 22 GB GPU belleği istiyor ve yalnızca Apple Silicon üzerinde çalışıyor.

| Adım | Model | Nerede |
|---|---|---|
| Konuşmayı yazıya dökme | Whisper large-v3-turbo (MLX) | Apple GPU, 2,5 GB |
| Taslak satırlar | NLLB-200 600M | Apple GPU |
| Nihai çeviri | qwen3.8 27B, sıkıştırılmış (IQ4_XS, `batiai/qwen3.8-27b:iq4`) | Apple GPU, 16,5 GB |
| Notlar | Aynı 27B | Apple GPU |

8 Ekim 2026'da kaydedilen gerçek Türkçe sesle her gün ve saat doğru çıktı. Ancak Whisper, on Türkçe satırdan dördünde yanlış kelime yazdı: "planlarından", gereksiz bir "bu", "müşteriyi ... duyacak" ve "küçüğü". Ayrıca Almanca "bis" (-e kadar) kelimesini "des" olarak duydu. Almanca çeviri, her Türkçe satırın anlamını korudu. Hem Türkçe metinde hem de notlarda, "çarşamba 16:00'a kadar" olan son tarih "saat 16:00'da" oldu. Video olduğu gibi bırakıldı.

Daha önce, yalnızca yapay seslerle yapılan denemede 21 satırın tamamı doğruydu ve son altyazılar, konuşmacı durduktan 1,2 ile 2,9 saniye sonra belirdi. Video yalnızca bunları gösteriyor.

Türkçe kayıtlar, Almanca sesin seviyesiyle eşleşmesi için 18 dB yükseltildi. Başlangıçta 19 dB daha sessizdiler ve bu seviyede, ilk kelime "Sürüm" üç denemeden ikisinde "Çürüm" gibi anlamsız bir kelimeye dönüştü. Gerçek bir aramada sessiz konuşandan sesini yükseltmesi istenir. Ses kaydının düzenlenmesini gerektiren bir süreç çözüm değildir ve gerçek bir toplantı bundan çok daha az kontrollüdür.

```
stream.py --live loopback --web --languages tr,de --glossary glossary.txt --log t.txt
notes.py t.txt --glossary glossary.txt
```

### Gerçek ses için tasarım düzeltmeleri ve çözemedikleri

Bu değişiklikleri, kaydedilen sesi sistemden yeniden geçirerek ölçtüm. Bu yeniden oynatma, canlı çalıştırmanın sonucunu kelimesi kelimesine aynen verir. Bir ayarı iki kez çalıştırdığımda, her iki deneme de aynı sonucu verdi.

**Çeviri bağlamı ve toplantı sözlüğü.** Çevirmen artık önceki iki satırı ve kısa bir sözlüğü görüyor. Bunu `--glossary` seçeneğiyle kullandım; her satırda bir `term = Begriff` yazdım. İlk kayıt, "geri dönüş seçeneği / yayın" ifadesini "Rückgabeoption nach der Ausstrahlung" (yayın sonrası iade seçeneği) olarak çevirdi. Bağlam ve sözlükle birlikte sonuç "Rollback-Option nach der Veröffentlichung" oldu. Sözlüğü, ilk kayıttaki hataları gördükten sonra yazdım. "kapsam = Umfang" girdisi, Almanca çevirinin "küçüğü" hatasına rağmen doğru çıkmasının kısmen nedenidir. Gerçek bir toplantıda bu listenin önceden yazılması gerekir ve yalnızca önceden tahmin edilen terimlerde işe yarar.

**Her cümleden önce kısa bir sesi saklamak.** Konuşmayı algılayan parça, ilk kelime başladıktan biraz sonra devreye girdiği için ondan önceki ses atılıyordu. Sessiz kayıtlarda "Sürüm" kelimesindeki "S" harfi o 64 milisaniyenin içindeydi. Şimdi kesimden önce 0,3 saniyeyi koruyorum. "Sürüm"ü asıl düzelten şey seviyeydi. Eşleşen seviyede, korunan ses süresi ne olursa olsun (0, 0,1, 0,2 ve 0,3 saniye) doğru çıktı. Süre yalnızca diğer Türkçe kelimelerin hangisinin değiştiğini etkiledi; örneğin "düzeltirim" yerine "düzeldir" ya da "duyuracak" yerine "duyacak" gibi. Hiçbir süre, her iki kayıtta da temiz değildi. Bir kelimenin başını atmak tasarım gereği yanlış olduğu için 0,3 saniyeyi korudum, ölçümün daha iyi olduğu için değil.

**Whisper'a sözlükten ipucu vermek (kullanılmadı).** Whisper'a cümlenin dilindeki sözlük terimlerini verdiğimde "Çürüm" üç denemede üç kez düzeldi. Ama bir sonraki düzeltmede "Haklısın" kelimesini iki denemede iki kez düşürdü.

**Daha büyük bir model.** `--whisper large-v3` bayrağıyla tam Whisper large-v3 modelini kullandım. Demo kaydını tekrar oynattığımda "bu", "müşteriyi" ve "duyacak" kelimelerini düzeltti. "küçüğü" ve "des" kelimelerini düzeltmedi. Satır başına yaklaşık 1,6 saniye sürdü; turbo ise yaklaşık 1,2 saniye sürüyordu. Aynı kliplerin önceki kaydında "düzeltirim" kelimesini bozdu. Daha iyi ama doğru değil. Canlı olarak çalıştırmadım.

**Güven puanıyla çözülemeyen.** "küçüğü" kelimesinde Whisper, yanlış olduğu yerde en yüksek güveni gösteriyor. Düşük güven bayrağı bunu yakalayamaz. Tasarım yanıtı, konuşanların kendi kelimelerini ekranda görüp yanlışsa tekrar etmesidir. Konuşan birinden bu kadarını beklemek çok şey istemektir.

### Aynı kayıtta başka ses modelleri

Turbo, yerelde çalışan en iyi model mi? Emre Akgül'ün bağımsız Türkçe sıralaması buna cevap veriyor. Her model için aynı testi kullanıyor: FLEURS, sesli okunan cümlelerden oluşan açık bir set, aynı şekilde puanlanıyor. Listenin başında Whisper large-v3 yüzde 5,66 kelime hatasıyla geliyor; ardından large-v3-turbo yüzde 6,07, Meta Omnilingual 7B yüzde 6,09 ve Qwen3-ASR 1.7B yüzde 8,46 ile devam ediyor. Yerelde çalışan modeller arasında bağımsız kanıtlarla Whisper en iyi durumda.

https://huggingface.co/spaces/EmreAkgul/Turkish-transcription-leaderboard

Demo kaydını dört modelde daha çalıştırdım; cümleler canlı çalıştırmadaki gibi kesildi: toplantının 19 cümlesi (10 Türkçe, 9 Almanca) ve bir Almanca ısınma cümlesi. 10 Türkçe cümledeki yanlış yazılan kelimeleri saydım. Büyük harf, noktalama veya rakam ile kelime farkını saymadım. Ayrıca anlamı değiştiren iki kelimeyi ve cümle başına geçen süreyi not ettim.

| Model | Yanlış kelimeler | "küçük" | Almanca "bis" | Cümle başına saniye |
|---|---|---|---|---|
| large-v3-turbo (video) | 5: planlarından, bu, müşteriyi, duyacak, küçüğü | yanlış | "des" | 0,7 |
| large-v3 | 2: planlandan, küçüğü | yanlış | "des" | 1,6 (başka Mac) |
| BuzzASR (Türkçe için ayrıca eğitilmiş large-v3) | 2: planlandan, küçüğü | yanlış | "des" | 1,1 |
| TurkMedSTT (Türkçe için ayrıca eğitilmiş large-v3) | 3: planlandan, düzeldir, küçüğü | yanlış | "des" | 1,2 |
| Qwen3-ASR 1.7B | 4: Tesel, Tesr, sorununu, mız | doğru | doğru | 0,5 |

Türkçe için ayrıca eğitilmiş iki sürüm, kendi yayınladıkları ölçümlerde large-v3'ü geçiyor ama benim kaydımda geçemiyor ve bağımsız sıralamada yer almıyor. İkisi de Almancaya zarar vermedi.

Qwen3-ASR (Alibaba'nın konuşmayı yazıya döken modeli), anlamı değiştiren iki kelimeyi de doğru yazan tek model; ama "Testler" öznesini iki kez bozdu. Yanlışları başka yerlerde; genel olarak daha iyi değil.

**Hiçbir model hatasız değildi ve yanlışları farklı yerlerde yaptılar.** turbo'nun ve Qwen3-ASR'ın her hatası, iki modelin uyuşmadığı bir kelime üzerindeydi; uyuştukları her cümle doğruydu. Bu tek bir toplantı ve 19 cümle, yani bir laboratuvar notu, sonuç değil. Bir güven puanı "küçüğü"nü işaretleyemezdi, çünkü Whisper tam orada en emin görünüyordu; bunu ikinci, farklı bir model yaptı. Bunu henüz yapmadım.

Mac'in GPU'sunda çalıştırmak için, Türkçe için eğitilmiş iki sürüm Apple'ın `mlx-examples/whisper/convert.py` dosyasıyla, sadece safetensors dosyalarından dönüştürüldü. Qwen3-ASR ise kendi `qwen-asr` paketiyle Apple GPU'sunda, bu projenin dışında çalıştı.

### Güvence: gün, saat ve sayılar kodla denetlenir

Denediğim her modelde, 27B dahil, çeviri sırasında gün veya saat değişti. "Mittwoch" (çarşamba) "salı" oldu, kimse söylemediği halde "dün" çıktı, 16:00 ise "4"e dönüştü. Modelden dikkatli olmasını istemek bu hatayı durdurmadı. Bu yüzden `facts.py` dosyası, her çeviriyi söylenenlerle karşılaştırır. Günler, "dün", "bugün" ve "yarın" gibi kelimeler, günün bölümleri ve rakam veya kelime olarak söylenen sayılar; Türkçe, Almanca ve İngilizce olarak kontrol edilir. Ardından şu adımlar izlenir:

- **Gün veya saat düzeltmesi:** Günlerin yer değiştirmesi veya 12 saatlik saat düzeninde okunan saatler, orijinal kayıttan alınarak düzeltilir.
- **Alternatif çeviri:** Düzeltme yapılamıyorsa başka bir çevirmen kullanılır ya da satır çevrilmeden bırakılır. Kendi dilinde kalan bir satır eksiktir; yanlış bir gün ise yanlış bir kayıttır.

`notes.py` dosyası da aynı denetimi yapar ve notlarda kimse söylemediği halde geçen gün veya sayıları işaretler.

**Yakalayamadıkları:** Başka bir konu için söylenmiş ama yanlış yere yazılmış bir tarih; hiç alınmamış bir kararın model tarafından alınmış gibi gösterilmesi; gün, saat veya sayı olmayan her şey. **Notları göndermeden önce dökümle karşılaştır.**

### Laboratuvar notları: daha küçük kurulumlar

Aynı hattın daha az bellekle ne kadar yol alabildiğini ölçtüm ve nerede koptuğunu görmek istedim. Bunlar, senaryolu toplantıdaki gözlemlerimdir, öneri değildir. Demo kurulumu bile gerçek konuşmada kanıtlanmadıysa, daha küçük olanlar hiç kanıtlanmamış sayılır.

#### Konuşmayı yazıya dökme

Whisper'ı (açık kaynaklı bir konuşma-yazı modelini) CPU üzerinde, faster-whisper ve int8 sıkıştırmasıyla çalıştırdım. Toplantıyı, canlı sürümdeki gibi cümle cümle böldüm. Kelime hata oranları şöyle:

| | Türkçe | Almanca | İngilizce | Bir saniyelik ses için gereken saniye |
|---|---|---|---|---|
| small | **%20,8** | %3,0 | %3,4 | 0,26 |
| medium | %2,3 | %1,8 | %4,0 | 0,80 |
| large-v3-turbo | %1,5 | %0,6 | %4,5 | 1,31 |

Her dilde aynı 18 cümle vardı ve tek bir yapay ses ailesi kullandım. İngilizce hatalarının çoğu, "14:00" yerine "1400 hours" yazılmasıydı. Zayıf halka model boyutu değil, Türkçe. Small modeli Almanca ve İngilizce için yeterli ama Türkçeyi anlamsız bir hale getiriyor; "cuma saat 14'te" yerine "Cumás-ı Atom 4'te" yazıyor. Whisper, İngilizce ve Almancaya kıyasla çok daha az Türkçe veriyle eğitildi. Türkçe için ayrıca eğitilmiş iki small sürümü daha kötü sonuç verdi; hata oranları %24 ve %45 oldu, biri de tümüyle uydurma cümleler üretti. Medium ve turbo Türkçede yeterince iyi ama CPU'da canlı akışı takip edemiyor, çünkü gecikme 186 saniyeye kadar çıktı.

Apple GPU'sunda turbo rahatça yetişiyor; 30 saniyelik sesi 2,3 saniyede, 2,5 GB bellekle işliyor. Belleğe asıl ihtiyacı olan Whisper değil, çeviri modeli.

#### Çeviri

`facts.py` içindeki gerçeklik kontrolünden önceki ham gün ve sayı hataları şöyle:

| Model | Nerede | Yüklenen boyut | Satır başına saniye | Hatalar |
|---|---|---|---|---|
| qwen3.8 27B IQ4_XS | GPU | 16,5 GB | yaklaşık 1,4 | 5 Ekim'de 90'da 0, 6 Ekim'de 54'te 2 |
| qwen3.8 27B Q4_K_M | GPU | 17,4 GB | yaklaşık 1,9 | 90'da 8 |
| TranslateGemma 12B | GPU | 9,0 GB | 0,61 | 21'de 0 |
| Aya Expanse 8B | GPU | 6,4 GB | 0,26 | 54'te 0 |
| TranslateGemma 4B | GPU | 3,3 GB | 0,25 | 21'de 4 |
| NLLB-200 600M | GPU / CPU | yaklaşık 2,4 GB | 0,24 | 18'de 1 |
| Opus-MT, İngilizce üzerinden Türkçe-Almanca | CPU | her biri yaklaşık 0,3 GB | 0,21 | 18'de 2 |
| qwen3.5 9B / 4B, qwen2.5 14B / 7B | GPU | 3 ila 9 GB | ölçülmedi | her çalıştırmada yanlış gün adları |

Gerçeklik kontrolü işin yalnızca yarısı. Aynı 21 cümlede satır satır karşılaştırdığımda, 27B model 8 satırda Aya 8B'den daha iyi, 3 satırda daha kötü okundu. Boşluğun çoğu Almancadan Türkçeye çeviride; daha küçük modeller kelime kelime çeviriyor, "Ich dachte ..." (I thought ...) için "Düşündüm ki ... dedik", "Gut" (Good) için "İyi" yazıyor. TranslateGemma 12B, Aya'dan daha doğal Türkçe yazıyor ama Aya'nın yapmadığı hatalar yapıyor, örneğin "demiştiğimiz" ve "separately" için "nochmals". NLLB harfiyen çeviriyor ve bazen düpedüz yanlış yazıyor, "görsel sorun" (visual issue) için "Augenlicht" (eyesight) gibi. "geri dönüş seçeneği" (rollback option) cümlesini ise hiçbir model doğru çeviremedi.

Bu toplantıda daha küçük bir kurulumun verdiği sonuçlar, kabaca şöyle:

| GPU belleği | Çeviri | Gözlenen |
|---|---|---|
| yaklaşık 6 GB | turbo + NLLB | harfiyen, bazen yanlış ifade; gerçeklik kontrolü tuttu |
| yaklaşık 11 GB | turbo + Aya 8B | doğru ama Almancadan Türkçeye çeviri hantal |
| yaklaşık 22 GB | turbo + 27B | en doğal; demo |
| yalnızca CPU | small + NLLB | Türkçe altyazılar kullanılamaz |

Bunların her biri bu toplantıda bir veya iki kez canlı çalıştırıldı. Yalnızca 22 GB'lık olanı demo.

#### Notlar

Notlar toplantıdan sonra yazıldığı için hız önemli değil. 27B ve Aya 8B ile, senaryolu toplantının notları, 0,1 sıcaklıkta kontrol ettiğim her çalıştırmada toplantıyla uyumlu çıktı. 0,3 sıcaklıkta Aya, 5 çalıştırmadan 1'inde açık soruyu bir karara dönüştürdü. qwen2.5 7B ise bir son tarihi yanlış güne taşıdı.

Canlı çevirisi geri çekilen bir satır, notlar yazılmadan önce, aynı kontrol altında notlar modeli tarafından yeniden çevriliyor. Aksi halde o satır, yani Almanca söylenen bir son tarih, her not setinden dışarıda kalıyordu.

### Ölçüm yaparken yaptığım hatalar

Benzer bir şeyi kendin deneyeceksen, bu dersler sayılardan daha önemli.

**Tam klip yanıltır.** Her deneme klipi iki cümle içeriyordu ve Whisper small bunları doğru yazıya döktü. Canlı bir aramadaki gibi tek cümlelere bölünce ise bunu yapamadı. Sesin gerçekten izlediği yolu ölç.

**Temiz dönüşüm yanıltır.** ffmpeg ile dönüştürülen klipler, Loopback üzerinden kaydedilen aynı kliplere kıyasla Whisper için daha iyi görünüyordu. Mac'ten 16 kHz istemek, 6 ile 8 kHz arasındaki enerjinin yarısını kaldıran bir filtreyle yeniden örnekleme yapmasına neden oldu; "t" ve "k" sesleri tam da bu aralıkta yaşar. Bu proje artık cihazın kendi hızında kaydeder ve soxr ile dönüştürür.

**Temiz bir çalışma bir özellik değildir.** 27B model bir gün 90 satırda 0 hata, ertesi gün 54 satırda 2 hata yaptı. Birden fazla kez çalıştır.

**Kaydı değil, ekranı kontrol et.** İki kayıtta döküm doğruydu ama sayfa değildi. Okunabilirlik için geri tutulan bir yeniden yazım, taslağın bitmemiş orijinalini nihai çevirinin yanında bıraktı.

**Sessiz bir konuşmacı farklı bir testtir.** Gerçek Türkçe ses, yapay Almanca sesin 19 dB altında geldi. Türkçenin zor olduğu izleniminin yarısı aslında sadece seviyeyle ilgiliydi.

**Her değişiklik başka bir kelimeyi değiştirir.** On Türkçe satırda, bir kelimeyi düzelten her ayar başka birini bozdu. Bu durumda bir sabit seçmek, gürültüye uydurmaktır. Bir düzeltmenin, ölçüm olmadan da geçerli olan bir nedeni olmalı.

### Denemediklerim

Spontane konuşmayı denemedim, çünkü gerçek ses bir metni okudu. İki kişiden fazla katılımcıyı, üst üste binen konuşmaları, aksanları, gürültüyü ve farklı mikrofonları da test etmedim. Uzun konuşmalar, konuşanları birbirinden ayırmak (altyazılar kişiyi değil, dili gösteriyor) ve gerçek bir Zoom görüşmesi de bu denemenin parçası değildi. Windows, Linux, NVIDIA grafik kartları ve daha az belleğe sahip Mac'lerde de çalıştırmadım. Üç dakikayı aşan hiçbir kaydı denemedim.

`--record` bayrağı, Ctrl-C ile durdurulana kadar girdiye ulaşan her şeyi kaydeder. Her dakika, o ana kadar geçen süreyi ekrana yazar. Bir toplantıyı kaydetmenin, ülkeden ülkeye değişen onay kuralları vardır.

---

## English

> **This is a proof of concept, not a product.** Everything below was measured on one scripted meeting, read from a script by one real voice and one artificial voice. Earlier runs used only artificial voices. This shows the pieces can be put together and run on one machine. It does not show that live captions or meeting notes work in a real meeting, including the setup in the demo video. Read the numbers as lab notes.

### What was tested

I tested one project-review meeting. It had 18 short turns, with one speaker in Turkish and one in German. Both parts were written in advance. In the demo video, the Turkish voice is mine, read from the script and recorded at home on one microphone. The German voice is an artificial voice, made with Piper (a program that turns text into speech), with the voice `de_DE-thorsten-high` (free to use, CC0). The measurements in the lab notes below were made earlier, using only artificial voices. I used Speechelo for most of them, and the built-in macOS voices for the three-language test. The audio was played into Loopback (a program that passes audio from one app to another) and captured live on an M4 Max MacBook Pro with 64 GB of memory.

This is the easiest case there is. The conditions were very controlled:

- **Clean pauses**: The script set the pauses between turns, so every sentence was cut exactly where it ended.
- **No overlap or hesitation**: Nobody said "ehm", started again, or talked over someone else.
- **One voice per language**: No accents. The Turkish voice was recorded in a room on one microphone; the German voice was artificial.
- **Three-second pauses**: I put these between turns so the translation appeared before the reply.
- **Short sentences**: None were long enough to hit the 6-second forced cut.
- **No names or jargon**: The only technical term was "release notes".

Real conversations have all of these. Each one is a known way for speech recognition to fail, and none of them was tested here. I did one informal run on a podcast on 9 September, translating English to Turkish. It ran without errors on screen, but I did not measure it.

### What the demo video shows

The video walks through four steps, all running on an Apple GPU. First, Whisper large-v3-turbo (a faster version of OpenAI's open speech-to-text model) turns speech into text, using 2.5 GB of memory. Next, NLLB-200 600M (Meta's translation model) shows a quick draft of each line. Then qwen3.8 27B (a large language model, here in a compressed version) writes the final translation and the notes, using 16.5 GB. In total, the setup needs about 22 GB of GPU memory and works only on Apple Silicon.

| Step | Model | Where |
|---|---|---|
| Speech to text | Whisper large-v3-turbo (MLX) | Apple GPU, 2.5 GB |
| Draft lines | NLLB-200 600M | Apple GPU |
| Final translation | qwen3.8 27B, compressed (IQ4_XS, `batiai/qwen3.8-27b:iq4`) | Apple GPU, 16.5 GB |
| Notes | the same 27B | Apple GPU |

With the real Turkish voice recorded on 8 October 2026, every day and time was correct. However, Whisper wrote a wrong word on four of the ten Turkish lines: "planlarından", a stray "bu", "müşteriyi ... duyacak", and "küçüğü". It also heard the German word "bis" (by) as "des". The German translation still carried the meaning of every Turkish line. In both the Turkish text and the notes, the deadline "by Wednesday 16:00" became "at 16:00". The video is left as it is.

Earlier, using only artificial voices, all 21 lines were correct, and the final captions appeared 1.2 to 2.9 seconds after the speaker stopped. That is all the video shows.

The Turkish recordings were raised by 18 dB to match the German voice’s level. They were originally 19 dB quieter, and at that level, the first word "Sürüm" came out as the non-word "Çürüm" on two of three plays. In a real call, a quiet speaker is asked to speak up. A pipeline that needs its audio edited is not a fix, and a real meeting is far less controlled than this.

```
stream.py --live loopback --web --languages tr,de --glossary glossary.txt --log t.txt
notes.py t.txt --glossary glossary.txt
```

### Design fixes for the real voice, and what they did not fix

I measured these changes by playing the recorded audio through the pipeline again. This replay reproduces a live recording word for word. Where I ran a setting twice, both runs were identical.

**Translation context and a meeting glossary.** The translator now sees the two previous lines and a short glossary. I used the `--glossary` flag, with one `term = Begriff` per line. The first recording turned "geri dönüş seçeneği / yayın" (rollback option / release) into "Rückgabeoption nach der Ausstrahlung" (return option after the broadcast). With context and the glossary, it became "Rollback-Option nach der Veröffentlichung". I wrote the glossary after seeing the mistakes in the first recording. The entry "kapsam = Umfang" is partly why the German survives "küçüğü". In a real meeting, this list has to be written in advance and only helps with terms you have foreseen.

**Keeping a moment of audio before each sentence.** The voice detector fires a little into the first word, so the audio before it was thrown away. On the quiet recordings, the "S" of "Sürüm" was in those 64 milliseconds. I now keep 0.3 seconds before the cut. What actually fixed "Sürüm" was the level. At the matched level, it was right at every length of kept audio: 0, 0.1, 0.2, and 0.3 seconds. The length only moved which other Turkish word flipped, such as "düzeldir" for "düzeltirim" or "duyacak" for "duyuracak". No length was clean on both recordings. I kept 0.3 seconds because throwing away the start of a word is wrong by design, not because it measured better.

**Whisper vocabulary prompt (not built).** Giving Whisper the glossary's terms in the sentence's language fixed "Çürüm" three times out of three. But it dropped "Haklısın" (you're right) from the next correction, two times out of two.

**A bigger model.** I used the full Whisper large-v3 model with the `--whisper large-v3` flag. Playing the demo recording again, it fixed "bu", "müşteriyi", and "duyacak". It did not fix "küçüğü" or "des". It took about 1.6 seconds per line, against turbo's about 1.2 seconds. On the earlier recording of the same clips, it broke "düzeltirim". It is better, but not right. I did not run it live.

**Not fixable by confidence.** On "küçüğü", Whisper is most confident where it is wrong. A low-confidence flag would not catch it. The design answer is that speakers see their own words on screen and repeat them when they are wrong. This is asking a lot of someone who is talking.

### Other speech models on the same recording

Is turbo the best model that runs locally? An independent Turkish ranking by Emre Akgül gives an answer. It uses the same test for every model: FLEURS, a public set of sentences read aloud, scored the same way. It lists Whisper large-v3 at 5.66 percent word errors, large-v3-turbo at 6.07 percent, Meta Omnilingual 7B at 6.09 percent, and Qwen3-ASR 1.7B at 8.46 percent. Among models that run locally, Whisper is the best with independent evidence.

https://huggingface.co/spaces/EmreAkgul/Turkish-transcription-leaderboard

I played the demo recording again through four more models, with the sentences cut exactly as in the live run: the meeting's 19 sentences (10 in Turkish, 9 in German) and one German warm-up sentence. I counted the wrongly written words in the 10 Turkish sentences. I did not count case, punctuation, or digits versus words. I also noted the two words that change the meaning and the time per sentence.

| Model | Wrong words | "küçük" | German "bis" | seconds per sentence |
|---|---|---|---|---|
| large-v3-turbo (the video) | 5: planlarından, bu, müşteriyi, duyacak, küçüğü | wrong | "des" | 0.7 |
| large-v3 | 2: planlandan, küçüğü | wrong | "des" | 1.6 (other Mac) |
| BuzzASR (large-v3 trained further for Turkish) | 2: planlandan, küçüğü | wrong | "des" | 1.1 |
| TurkMedSTT (large-v3 trained further for Turkish) | 3: planlandan, düzeldir, küçüğü | wrong | "des" | 1.2 |
| Qwen3-ASR 1.7B | 4: Tesel, Tesr, sorununu, mız | right | right | 0.5 |

The two versions trained further for Turkish beat large-v3 in their own published measurements, but not on my recording, and they are not on the independent ranking. Neither of them harmed the German.

Qwen3-ASR (Alibaba's speech-to-text model) is the only one that got both meaning-changing words right, but it garbled the subject "Testler" twice. It is wrong in different places, not better overall.

**No model was free of mistakes, and they were wrong in different places.** Every mistake of turbo and of Qwen3-ASR sat on a word where the two models disagreed, and every sentence they agreed on was right. This is one meeting and 19 sentences, so it is a lab note, not a result. A confidence score could not flag "küçüğü", because Whisper was most confident exactly there; a second, different model did. I have not built this.

To run on the Mac's GPU, the two versions trained for Turkish were converted with Apple's `mlx-examples/whisper/convert.py`, from their safetensors files only. Qwen3-ASR ran through its own `qwen-asr` package on the Apple GPU, outside this project.

### The safeguard: facts are checked in code

Every model I tried, the 27B included, at some point changed a day or a time while translating: "Mittwoch" (Wednesday) became "Salı" (Tuesday), a "yesterday" appeared that nobody said, 16:00 became "4". Asking a model to be careful did not stop it. So `facts.py` compares each translation with what was said: weekdays, words like yesterday, today and tomorrow, parts of the day, and numbers in digits or words, in Turkish, German and English. Then it:

- repairs a swapped weekday, or a time read on a 12-hour clock, from the original;
- otherwise uses another translator, or shows the line untranslated. A line in its original language is incomplete; a wrong day is a false record.

`notes.py` uses the same check, and flags any day or number in the notes that nobody said.

**What it cannot catch:** a fact that was said, but for something else (a deadline moved to the wrong task); a decision that was never made (a model once turned an open question into one); anything that is not a day, a time or a number. **Read the notes against the transcript before sending them.**

### Lab notes: smaller setups

I measured how far the same pipeline gets with less memory to see where it breaks. These are observations on the scripted meeting, not recommendations. If the demo setup is unproven on real speech, the smaller ones are even less so.

#### Speech to text

I ran Whisper (an open speech-to-text model) on the CPU using faster-whisper and int8 compression. I cut the meeting into sentences exactly as in the live version. Here is the word error rate:

| | Turkish | German | English | Seconds of work per second of audio |
|---|---|---|---|---|
| small | **20.8%** | 3.0% | 3.4% | 0.26 |
| medium | 2.3% | 1.8% | 4.0% | 0.80 |
| large-v3-turbo | 1.5% | 0.6% | 4.5% | 1.31 |

Each language had the same 18 sentences, and I used one synthetic voice family. English errors were mostly "1400 hours" written for "14:00". The weakness is Turkish, not model size. The small model is fine for German and English but turns Turkish into nonsense, writing "Cumás-ı Atom 4'te" for "cuma saat 14'te" (Friday at 14:00). Whisper was trained on far less Turkish than English or German. Two versions of the small model trained further for Turkish did worse, with 24% and 45% error rates, and one invented whole sentences. Medium and turbo are good enough on Turkish but cannot keep up live on a CPU, as the lag grew to 186 seconds.

On the Apple GPU, turbo keeps up easily, processing 30 seconds of audio in 2.3 seconds with 2.5 GB of memory. It is the translation model, not Whisper, that needs the memory.

#### Translation

Here are the raw day and number errors, before the facts check in `facts.py`:

| Model | Where | Size loaded | Seconds per line | Errors |
|---|---|---|---|---|
| qwen3.8 27B IQ4_XS | GPU | 16.5 GB | about 1.4 | 0 of 90 on 5 Oct, 2 of 54 on 6 Oct |
| qwen3.8 27B Q4_K_M | GPU | 17.4 GB | about 1.9 | 8 of 90 |
| TranslateGemma 12B | GPU | 9.0 GB | 0.61 | 0 of 21 |
| Aya Expanse 8B | GPU | 6.4 GB | 0.26 | 0 of 54 |
| TranslateGemma 4B | GPU | 3.3 GB | 0.25 | 4 of 21 |
| NLLB-200 600M | GPU / CPU | about 2.4 GB | 0.24 | 1 of 18 |
| Opus-MT, Turkish to German via English | CPU | about 0.3 GB each | 0.21 | 2 of 18 |
| qwen3.5 9B / 4B, qwen2.5 14B / 7B | GPU | 3 to 9 GB | not measured | wrong weekdays in every run |

Facts are only half of it. Line by line on the same 21 sentences, the 27B model read better than Aya 8B on 8 lines and worse on 3. Most of the gap is German to Turkish, where the smaller models translate word by word, writing "Düşündüm ki ... dedik" for "Ich dachte ..." (I thought ...) and "İyi" for "Gut" (Good). TranslateGemma 12B wrote more natural Turkish than Aya but made errors Aya did not, such as "demiştiğimiz" and "nochmals" for "separately". NLLB is literal and sometimes simply wrong, writing "Augenlicht" (eyesight) for "görsel sorun" (visual issue). One line, "geri dönüş seçeneği" (rollback option), no model translated correctly.

Here is what a smaller setup gave on this meeting, roughly:

| GPU memory | Translation | Observed |
|---|---|---|
| about 6 GB | turbo + NLLB | literal, sometimes wrong wording; facts held |
| about 11 GB | turbo + Aya 8B | correct but clumsy German to Turkish |
| about 22 GB | turbo + 27B | the most natural; the demo |
| CPU only | small + NLLB | Turkish captions unusable |

Each of these ran live on this meeting once or twice. Only the 22 GB one is the demo.

#### Notes

The notes are written after the meeting, so speed does not matter. With the 27B and with Aya 8B, the notes from the scripted meeting matched it in every run I checked, at temperature 0.1. At 0.3, Aya turned the open question into a decision in 1 run of 5. qwen2.5 7B moved a deadline to the wrong day.

A line whose live translation was withheld is translated again by the notes model, under the same check, before the notes are written. Otherwise that line, a deadline in German, was left out of every set of notes.

### Mistakes I made measuring

These lessons matter more than the numbers if you try something similar yourself.

**Whole clips flatter.** Each test clip held two sentences, and Whisper small got them right. Cut into single sentences, as in a live call, it did not. Measure the path the audio really takes.

**Clean conversions flatter.** Clips converted with ffmpeg sounded better to Whisper than the same clips captured through Loopback. Asking the Mac for 16 kHz let it resample with a filter that removed half the energy between 6 and 8 kHz, where "t" and "k" live. This project now captures at the device's own rate and converts with soxr.

**A clean run is not a property.** The 27B model made 0 errors in 90 lines one day and 2 in 54 the next. Run more than once.

**Check the screen, not the log.** For two recordings, the transcript was right and the page was not. A rewrite held back for readability kept the draft's unfinished original next to the final translation.

**A quiet speaker is a different test.** The real Turkish voice arrived 19 dB below the synthetic German one. Half of what looked like Turkish being hard was just level.

**Every change flips some other word.** On ten Turkish lines, each setting that fixed one word broke another. Choosing a constant on that is fitting noise. A fix needs a reason that holds without the measurement.

### What I did not test

I did not try spontaneous speech, because the real voice read a script. I also did not test more than two people, overlapping speech, accents, noise, or other microphones. Long monologues, telling speakers apart (the captions show the language, not the person) and a real Zoom call were not part of this experiment. I did not run it on Windows, Linux, NVIDIA GPUs, or Macs with less memory. Anything over three minutes was not tested.

The `--record` flag records everything that reaches the input until it is stopped with Ctrl-C. It prints the running length every minute. Recording a meeting has consent rules that vary by country.
