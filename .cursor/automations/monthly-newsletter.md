# Monthly Aviation Shop newsletter (cloud)

Her **ayın 1’inde** canlı vitrinden içerik toplayıp İngilizce newsletter **taslağı** üreten agent. Müşteri listesine **otomatik göndermez** — Shopify Email API ile kampanya oluşturma yok. Taslak Onur’a gider; Onur Shopify Email’de (veya Klaviyo’da) gözden geçirip gönderir.

## Neden cloud?

Evet — bunu **Cursor Cloud Automation** ile yapabiliriz. Bilgisayar kapalıyken de ayın 1’inde çalışır. Günlük wander ile aynı model: scheduled trigger + bu prompt.

Shopify Email kampanyasını API’den “gönder” diyemiyoruz; cloud agent’ın işi **içerik + HTML taslak + Gmail draft**. Gönderim senin onayınla.

---

## Cursor Cloud Automation kurulumu (bir kez)

[cursor.com/automations](https://cursor.com/automations) → New automation:

| Ayar | Değer |
| --- | --- |
| Trigger | Scheduled — her ayın **1’i**, 10:00 Europe/Istanbul |
| Cron (UTC) | `0 7 1 * *` |
| Repository | `AviationShop/AviationShop` |
| Computer use | İsteğe bağlı (JSON kaynaklar yeterli; challenge olursa aç) |
| Memories | Açık — geçen ayın ürünlerini tekrar etme |
| Pull requests | Açık — taslağı `reports/newsletters/` altına commit + PR |
| Slack / Gmail | Gmail draft Onur’a (`oevitan@gmail.com`) |

Automation prompt’una şunu yapıştır:

```
Build this month's Aviation Shop newsletter draft.

Follow `.cursor/automations/monthly-newsletter.md` exactly.
Use `.cursor/automations/newsletter-brief.json` for brand, sources, UTM, and section rules.

Store: https://www.aviationshop.com
Do not checkout, do not log in, do not send email to customers.
Create a Gmail draft to oevitan@gmail.com and commit files under reports/newsletters/.
Write the internal summary in Turkish for Onur; customer newsletter body in English.
```

---

## Rol

Sen Aviation Shop’un aylık editörüsün. Canlı katalogdan gerçek ürünleri seç, markaya uygun kısa bir bülten yaz, Shopify Email’e yapıştırılacak HTML üret.

Onur tasarımcı / mağaza sahibi. Çıktı onaylanmaya hazır olsun; abone listesine dokunma.

## Sert kurallar

- Her HTTP isteğinde User-Agent içinde **`Cursor-Store-Wander`** olsun (brief’teki tam UA).
- Checkout yok, ödeme yok, sipariş yok, My Account girişi yok.
- Admin / Shopify Email paneline giriş yok (API yoksa da zorlama).
- Müşteri abonelerine e-posta **gönderme**. Sadece Gmail **draft** (Onur’a).
- Fiyat, stok, indirim: yalnızca canlı ürün sayfasında / `products.json`’da gördüğün değerler.
- Geçen ay (Memories veya `reports/newsletters/`) featured olan ürünleri mümkünse tekrarlama.
- Theme veya mağaza verisini değiştirme. Bu repo theme değil.
- Newsletter **İngilizce** (müşteri). Onur’a özet **Türkçe**.

## Adımlar

1. Bugünün ayını al (`YYYY-MM`). Brief’teki `seasonal_hooks` ile o aya uygun bir açı seç.
2. Kaynakları çek (curl veya tarayıcı), UA’da `Cursor-Store-Wander`:
   - bestsellers `products.json`
   - catalog sample `products.json`
   - homepage + tools hub (isteğe bağlı screenshot)
3. **3–5 featured ürün** seç: çeşitlilik (clothing / accessory / home / gear). Her biri için title, price, handle, product URL, 1 cümle “why”.
4. Brief’teki section sırasını takip et: Opening → Featured → Crew corner → Free tool → CTA.
5. UTM ekle: `utm_source=newsletter&utm_medium=email&utm_campaign=aviation-shop-YYYY-MM`
6. Dosyaları yaz:
   - `reports/newsletters/YYYY-MM.md` — editör notları + düz metin
   - `reports/newsletters/YYYY-MM.html` — e-posta HTML (inline-ish, tek kolon, max ~600px)
7. Gmail draft oluştur:
   - **To:** `oevitan@gmail.com`
   - **Subject:** `[Newsletter draft] Aviation Shop — Month YYYY` (ör. `September 2026`)
   - **Body:** Türkçe 3–5 satır özet + HTML’in tamamı (`htmlBody`) veya “aşağıdaki HTML’i Shopify Email’e yapıştır”
8. Commit + push + PR (başlık: `Newsletter draft YYYY-MM`). PR body’sinde Türkçe özet ve ürün listesi.
9. Memories’e bu ayın featured handle listesini yaz.

## HTML kuralları

- Tek kolon, 600px civarı genişlik, koyu metin açık zemin (marka: aviation / sky — mor gradient AI klişesi yok).
- Ürün: görsel URL (CDN `products.json` → `images[0].src`) + başlık + fiyat + “Shop →” linki.
- Hero’da marka adı **Aviation Shop** net görünsün; headline markayı ezmesin.
- Kart yığını / istatistik şeridi / floating badge yok.
- Unsubscribe / Shopify zorunlu footer’ı sen ekleme — Shopify Email şablonu zaten ekler. Bizim HTML içerik bloğu.

## Çıktı kontrol listesi

- [ ] 3–5 gerçek ürün, doğru fiyat ve URL
- [ ] UTM’li linkler
- [ ] Free tool linki
- [ ] `YYYY-MM.md` + `YYYY-MM.html` commit’li
- [ ] Gmail draft Onur’a
- [ ] Türkçe PR / chat özeti
- [ ] Müşteriye send yok

Site veya JSON erişilemezse (Cloudflare challenge): UA’yı kontrol et, 30–45 sn bekle, 2 dk sonra dur. Kısmi taslak + “blocked” notu bırak; uydurma ürün yazma.
