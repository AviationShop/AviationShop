# Daily Aviation Shop wander

Her gün `www.aviationshop.com` üzerinde **rastgele** dolaşan agent. Aynı rotayı ezberlemesin; her koşuda farklı kategori, ürün ve açıklama görsün.

## Senin Mac’in, her gün 10:00

Bu cloud sohbet senin bilgisayarını açamaz. 10:00’da **senin Chrome’un** çalışsın istiyorsan kurulumu bir kez Mac’te yap.

**A — Cursor Desktop (en kolay)**

1. Cursor’u kendi Mac’inde aç.
2. Chat’e yaz: `/automate her gün saat 10:00’da www.aviationshop.com’u rastgele gez, farklı ürün ve description’lara bak. Prompt: .cursor/automations/daily-store-wander.md`
3. Runtime olarak bu makineyi seçebiliyorsan seç. Computer use açık olsun.
4. Mac 10:00’da açık (veya uyandırılmış) olsun.

**B — macOS 10:00 alarmı (Cursor CLI)**

Mac Terminal’de, bu reponun klasöründe:

```bash
chmod +x scripts/macos/install-10am.sh scripts/macos/daily-store-wander.sh
./scripts/macos/install-10am.sh
```

Bu, her gün **yerel saat 10:00**’da `agent -p` ile wander’ı başlatır. Kaldırmak için: `./scripts/macos/uninstall-10am.sh`

Gerekli: [Cursor CLI](https://cursor.com/docs/cli/overview) (`curl https://cursor.com/install -fsS | bash`), bir kez `agent login`, Mac’in 10:00’da uyanık olması.

Cloudflare senin ev IP’nle genelde cloud agent’tan daha kolay geçer.

---

## Cloud Automation (bilgisayar kapalıyken)

[cursor.com/automations](https://cursor.com/automations) → New automation:

| Ayar | Değer |
| --- | --- |
| Trigger | Scheduled, her gün 10:00 Europe/Istanbul (`0 7 * * *` UTC) |
| Repository | `AviationShop/AviationShop` |
| Computer use | Açık |
| Memories | Açık — aynı ürünleri 14 gün tekrar etmesin |
| Pull requests | Kapalı (mümkünse). Prompt zaten PR yasaklıyor |
| Slack | İsteğe bağlı; günlük raporu kanala atsın |

Bu yol Cursor cloud tarayıcısını kullanır, senin Mac’ini değil. Cloudflare Turnstile cloud tarayıcıyı keserse vitrine giremez; o zaman A veya B’yi kullan.

Aşağıdaki kısa metni automation prompt’una yapıştır.

```
Wander the LIVE Aviation Shop storefront today. There is no product cap.

Follow `.cursor/automations/daily-store-wander.md` exactly: two departments, at least 10 products across three types, two searches, one tool, plus cart or content or mobile, and the developer checks on the pages you opened.
Use `.cursor/automations/wander-seeds.json` only as starting points.
Use Memories so you do not repeat products/collections from the last 14 days.

Store: https://www.aviationshop.com
Do not checkout, do not log in, do not open a pull request.
Write the daily report in Turkish for Onur.
```

---

## Rol

Onur tasarımcı. Aynı koşuda iki şapka tak: meraklı müşteri ve vitrini okuyan geliştirici. Katalog 100k+ ürün ve 1600+ koleksiyon. Limit yok — kısa bir sağlık check’i yetmez. Her koşuda sitenin **başka köşelerine** in, açıklamaları gerçekten oku, sayıları ve varyantları kontrol et. Bozuk, boş, çirkin, markaya uymayan, yanlış sayılan veya şablon kopyası olan her şeyi raporla.

Bu koşu bir geliştiricinin kendi makinesindeyse (Cursor Desktop veya `agent -p`), o makinenin tarayıcısını kullan. Cloud sandbox’taysan computer use kullan.

## Sert kurallar

- Gerçek tarayıcı veya curl kullan. Her istekte User-Agent içinde **`Cursor-Store-Wander`** olsun. Cloudflare WAF skip kuralı (Allow Cursor daily store wander) bunu geçer.
- Chrome/computer-use: User-Agent’ı `Mozilla/5.0 ... Cursor-Store-Wander ...` yap. Yoksa AWS IP’si “Big-cloud datacenter challenge” yer.
- Challenge hâlâ görünürse: UA’yı kontrol et, 30–45 sn bekle. 2 dakikadan fazla takılırsan dur; “site down” deme. GitHub issue açma.
- Checkout yok, ödeme yok, sipariş yok.
- My Account’a giriş yok.
- Live chat’e yazma; sayfayı kapatıyorsa kapat.
- Theme, ürün veya bu repoyu (wander dosyalarındaki yazım hatası hariç) değiştirme.
- Pull request açma. Bu repo Shopify theme’i değil. Vitrin bug’ları GitHub issue olur.
- Günlük rapor Türkçe. Ürün başlıklarını orijinal dilinde bırak.

## Bugünkü yolu nasıl seçersin (rastgele olmak zorunda)

1. Memories’den (veya `~/.aviationshop-wander-log.md` dosyasından) son 14 günde gezilen URL / collection / product handle listesini oku. Bunları tekrar açma (eski bir bug’ı doğrulamak hariç).
2. Şansı bugünün UTC tarihi (`YYYY-MM-DD`) ve saatten birkaç ekstra zar ile kur. Aynı gün iki koşu bile ayrışabilsin.
3. Önce homepage’i aç. Gerçek içerik gelene kadar bekle. Desktop screenshot al.
4. Dünkü departman çiftini tekrarlama. Aşağıdaki müşteri turunun **hepsini** çalıştır. Süre veya ürün sayısı için kendi kendine limit koyma; 14 günlük “görüldü” listesi tek tekrarsızlık kuralı.

### Müşteri turu (her gün, hepsi)

**A. İki departman**  
Header’dan dünden farklı **iki** üst kategori aç (Clothing, Key Chains, Phone Cases, Watches, Mugs, Models, Pilot Gear, Home, Bags, Jewelry, Car, Tools, vb.). Her birinde bir alt koleksiyona gir. Boş grid, kırık kart, eksik fiyat, üst üste yazı, hub’da 10 ürün ama kardeşte binlerce ürün not et.

**B. Ürün derin bakış**  
Son 14 günde görmediğin **en az 10 ürün**, en az **üç farklı tip** (ör. kupa + hoodie + anahtarlık). Her birinde: başlık, fiyat, compare-at, description, variant (beden / renk / airline / pack), galeri (2–3 görsel), “add your name” / LED / pack-size. Ürünle uyuşmayan generic copy, eksik görsel, yanlış livery, tekrarlayan paragraflar, kesilmiş metin, görünür “Your browser does not support the video tag”, seçilemeyen variant — bunları işaretle.

**C. İki arama**  
`wander-seeds.json` içindeki `search_queries` listesinden iki farklı sorgu, ya da benzer bir havacılık sorgusu. Her birinden 2 sonuca gir. Sonuç başlığındaki sayı tavanı (1000 / 1002) ve alakasız 10. sırayı not et.

**D. Bir araç**  
`wander-seeds.json` → `tools` listesinden son 14 günde açılmamış bir ücretsiz araç. Örnek değerin sonucunu kontrol et. 0’da kalan, input’u yok sayan veya hero’su “Quick aviation calculation” diye genel kalan aracı işaretle.

**E veya F veya G’den en az bir tane daha**  
İçerik sayfası (blog / About / Reviews), sepet duman testi (ekle ve çıkar, checkout yok), veya ~390px genişlikte aynı koleksiyon + PDP. Üçünü birden yapmak serbest.

### Geliştirici kontrolü (açtığın sayfaların üstünde, ayrı katalog taraması değil)

Açtığın koleksiyon ve ürünlerde şunları say. Şüpheyi bulgu diye yazma; sayıyı veya metni gördüğün şeyi yaz.

- Üst koleksiyon `products_count` ile bariz alt koleksiyon. Üst boş/çok küçük, alt doluysa hub hatası.
- Seçeneklerin kartezyen çarpımı ile `variants` uzunluğu. 250’de kesilen ürün (renk × beden × stil daha büyükse) varyant tavanı.
- `compare_at_price` satış fiyatının altındaysa yaz. $0 varyant yaz.
- Farklı başlıklı ürünlerde birebir aynı description HTML.
- Başlıktaki uçak, havayolu veya parça adı description’da yoksa yaz. Handle ile vitrin başlığı başka ürün konuşuyorsa yaz.
- Ham shortcode, “Made with passion”, “M aterial” gibi kırık boşluk, video-tag cümlesi.

**E. İçerik** — bir blog, About, Reviews veya Pilot Resources sayfası. Ölü link, kesik `<title>`.

**F. Sepet** — bir varyantı sepete ekle, başlık / fiyat / adet doğrula, çıkar. Checkout yok.

**G. Dar ekran** — aynı koleksiyon + bir PDP’yi ~390px genişlikte tekrar aç. Taşan header, okunmayan açıklama, kullanılamayan variant.

## Her üründe bakılacaklar

- Hero görsel yükleniyor, yeterince net, başlıkla uyumlu
- Galeride boş/kırık slot yok
- Başlık, description ve seçili variant aynı üründen bahsediyor
- İndirimli fiyat ve compare-at mantıklı ($0 değil; compare-at satış fiyatının altında değil)
- Description bu ürüne özel; “Made with passion…” gibi generic blok, asıl specleri yok sayıyorsa not düş
- Kişiselleştirme / beden / pack seçenekleri seçilebiliyor ve sayfayı güncelliyor
- Related products boş değil, aynı ürünün altı kopyası değil, konuyla ilgili
- Dev layout boşluğu, üst üste badge, `%AMOUNT%` gibi kalmış token yok

## Coverage memory

Gezinin sonunda Memories’e ve varsa `~/.aviationshop-wander-log.md` dosyasına ekle:

- tarih
- çalıştırılan görevler
- collection URL’leri
- product URL / handle’lar
- arama sorguları
- kullanılan araçlar
- bulunan bug’lar (issue açtıysan id)

14 günlük “görüldü” listesini tut. Pencerede hiç uğramadığın departmanlara yönel.

## Çıktı

Türkçe günlük rapor yaz (CLI koşusunda stdout + `~/Desktop/aviationshop-wander-YYYY-MM-DD.md` + PDF). Kısa tutmak için bulgu atlama.

1. **Bugün nereye gittim** — URL listesi, koleksiyon sayıları
2. **Ürün notları** — açtığın ürünler, her biri bir cümle (description, görsel, variant)
3. **Sorunlar** — sadece doğruladığın sorunlar, şiddet (blocker / görsel / copy / katalog). Yoksa: “Bugün blocker yok.”
4. **Yarın için** — son günlerde uğramadığın bir departman

Gerçek bir vitrin bug’ı varsa `AviationShop/AviationShop` içinde **tek** GitHub issue aç:

- Title: `[storefront] kısa açıklama`
- Body: URL, ne gördün, ne bekledin, varsa screenshot, tarih

Zevk meselesi, Cloudflare challenge, tek seferlik yavaş yükleme için issue açma.

Site temizse başka bir şey yapma. PR yok, ekstra dosya yok.
