# Daily Aviation Shop wander

Her gün `www.aviationshop.com` üzerinde **rastgele** dolaşan agent. Aynı rotayı ezberlemesin; her koşuda farklı kategori, ürün ve açıklama görsün.

## Cursor Automation ayarı

[cursor.com/automations](https://cursor.com/automations) → New automation:

| Ayar | Değer |
| --- | --- |
| Trigger | Scheduled, her gün 09:00 Europe/Istanbul (`0 6 * * *` UTC) |
| Repository | `AviationShop/AviationShop` |
| Computer use | Açık |
| Memories | Açık — aynı ürünleri 14 gün tekrar etmesin |
| Pull requests | Kapalı (mümkünse). Prompt zaten PR yasaklıyor |
| Slack | İsteğe bağlı; günlük raporu kanala atsın |

Aşağıdaki kısa metni automation prompt’una yapıştır. Agent bu dosyayı ve `wander-seeds.json` dosyasını repodan okur.

```
Wander the LIVE Aviation Shop storefront today.

Follow `.cursor/automations/daily-store-wander.md` exactly.
Use `.cursor/automations/wander-seeds.json` only as starting points.
Use Memories so you do not repeat products/collections from the last 14 days.

Store: https://www.aviationshop.com
Do not checkout, do not log in, do not open a pull request.
Write the daily report in Turkish for Onur.
```

---

## Rol

Onur tasarımcı. Sen meraklı bir müşteri gibi canlı vitrine girersin — sabit URL listesini tıklayan bir sağlık check’i değilsin. Katalog 100k+ ürün ve 1600+ koleksiyon. Her koşuda sitenin **başka bir köşesine** in, ürünleri ve description’ları gerçekten oku, bozuk / boş / çirkin / markaya uymayan her şeyi raporla.

## Sert kurallar

- Gerçek tarayıcı kullan (computer use). Cloudflare curl/fetch’i engeller; challenge bitene kadar bekle, sonra devam et. 2 dakikadan fazla challenge’da kalırsan bunu söyle ve dur.
- Checkout yok, ödeme yok, sipariş yok.
- My Account’a giriş yok.
- Live chat’e yazma; sayfayı kapatıyorsa kapat.
- Theme, ürün veya bu repoyu (wander dosyalarındaki yazım hatası hariç) değiştirme.
- Pull request açma. Bu repo Shopify theme’i değil. Vitrin bug’ları GitHub issue olur.
- Günlük rapor Türkçe. Ürün başlıklarını orijinal dilinde bırak.

## Bugünkü yolu nasıl seçersin (rastgele olmak zorunda)

1. Memories’den son 14 günde gezilen URL / collection / product handle listesini oku. Bunları tekrar açma (eski bir bug’ı doğrulamak hariç).
2. Şansı bugünün UTC tarihi (`YYYY-MM-DD`) ve saatten birkaç ekstra zar ile kur. Aynı gün iki koşu bile ayrışabilsin.
3. Önce homepage’i aç. Gerçek içerik gelene kadar bekle. Desktop screenshot al.
4. Aşağıdaki görevlerden **rastgele 2 veya 3** tanesini çalıştır. Dün çalıştırdığın çifti bugün tekrarlama.

### Görevler (2–3 tane seç)

**A. Mega-menu wander**  
Header’dan rastgele bir üst kategori aç (Clothing, Key Chains, Phone Cases, Watches, Mugs, Models, Pilot Gear, Home, Bags, Jewelry, Car, Tools, vb.). Sonra rastgele bir alt koleksiyona gir. En az iki ekran kaydır. Boş grid, kırık kart, eksik fiyat, üst üste binen yazı not et.

**B. Product deep-dive**  
Koleksiyon veya aramadan, son 14 günde görmediğin **4–6 ürün** aç. Her birinde: başlık, fiyat, compare-at fiyat, description, variant (beden / renk / airline), galeri (2–3 görsel), “add your name” / LED / pack-size seçenekleri. Ürünle uyuşmayan generic copy, eksik görsel, yanlış livery, tekrarlayan paragraflar, kesilmiş metin, görünür “Your browser does not support the video tag”, tıklanınca hiçbir şey yapmayan variant — bunları işaretle.

**C. Search wander**  
`wander-seeds.json` içindeki `search_queries` listesinden rastgele bir sorgu yaz (veya benzer bir havacılık sorgusu uydur). 2 sonuca gir. Boş veya bariz yanlış sonuç bir bulgudur.

**D. Tool wander**  
Aviation Tools menüsünden veya `wander-seeds.json` → `tools` listesinden rastgele bir ücretsiz araç aç. Örnek değer gir, sonucun güncellendiğini kontrol et, screenshot al. 0’da kalan, input’u yok sayan veya mobilde kırık araçları işaretle.

**E. Content wander**  
Rastgele bir blog yazısı, About, Reviews veya Pilot Resources sayfası aç. Layout, görseller, yazı içindeki ölü linkler.

**F. Cart smoke**  
Rastgele bir ürünü (variant varsa bir variant) sepete ekle, cart/drawer’ı aç, görsel / başlık / fiyat / adet doğrula, ürünü çıkar. Checkout yok.

**G. Mobile pass**  
Viewport ~390×844. Bugünkü yoldan bir koleksiyon + bir PDP’yi tekrarla. Header taşması, üst üste fiyatlar, okunmayan description, kullanılamayan variant picker.

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

Gezinin sonunda Memories’e ekle:

- tarih
- çalıştırılan görevler
- collection URL’leri
- product URL / handle’lar
- arama sorguları
- kullanılan araçlar
- bulunan bug’lar (issue açtıysan id)

14 günlük “görüldü” listesini tut. Pencerede hiç uğramadığın departmanlara yönel.

## Çıktı

Agent konuşmasına kısa Türkçe günlük rapor yaz:

1. **Bugün nereye gittim** — URL listesi
2. **Ürün notları** — 3–6 ürün, her biri bir cümle (description, görsel, variant)
3. **Sorunlar** — sadece gerçek sorunlar, şiddet (blocker / görsel / copy). Yoksa: “Bugün blocker yok.”
4. **Yarın için** — son günlerde uğramadığın bir departman

Gerçek bir vitrin bug’ı varsa `AviationShop/AviationShop` içinde **tek** GitHub issue aç:

- Title: `[storefront] kısa açıklama`
- Body: URL, ne gördün, ne bekledin, varsa screenshot, tarih

Zevk meselesi, Cloudflare challenge, tek seferlik yavaş yükleme için issue açma.

Site temizse başka bir şey yapma. PR yok, ekstra dosya yok.
