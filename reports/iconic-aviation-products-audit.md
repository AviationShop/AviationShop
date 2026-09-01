# Iconic Aviation Products — katalog taraması

Tarih: 2026-09-01  
Koleksiyon: https://www.aviationshop.com/collections/iconic-aviation-products  
Shopify `products_count`: **13 251**  
Bu raporda taranan: **5 950 ürün** (`products.json` sayfa 1–119). Aynı tasarım ~20 ürün tipine yayılıyor; bulunan hatalar sistematik.

User-Agent: `Cursor-Store-Wander`. Checkout / login yok.

## Temiz çıkanlar (taranan dilimde)

| Kontrol | Sonuç |
|---|---|
| Boş description (`body_html`) | 0 |
| Görselsiz ürün | 0 |
| $0 varyant | 0 |
| Yayınlanmamış ürün | 0 |
| Duplicate başlık | 0 |
| `copy` / `test` / `draft` başlık | 0 |

City Series Vertical Canvas’taki boş description burda yok. Description’lar uzun (medyan ~3900 karakter).

---

## 1) Double-Side Hoodie — XS yok

**355** hoodie:

- **179** Premium Zipped Hoodie → beden **XS–XXL** (tam)
- **176** Double-Side Hoodie → beden **S–XXL** (XS yok)

Double-Side hattında seçenekler Color(15) × Size(5) × Printing(2) = **150 varyant, hepsi var.** Eksik rastgele SKU değil; XS hiç tanımlanmamış.

Aynı koleksiyondaki Double-Side T-Shirt S–XXXL (XS yok — muhtemelen bilinçli). Polo S–3XL. Tutarsızlık hoodie’de: zipped’te XS var, double-side’da yok.

Örnek: https://www.aviationshop.com/products/roll-rate-rewrites-the-horizon-double-side-hoodie  
Karşılaştır: https://www.aviationshop.com/products/roll-rate-rewrites-the-horizon-premium-zipped-hoodie

PDP swatch’te de yalnızca S M L XL XXL var.

---

## 2) Phone / tablet / MacBook — Shopify 250 varyant tavanı

Storefront `product.js` ve `products.json` **ürün başına en fazla 250 varyant** döndürüyor. Tema picker’ı ise tüm option değerlerini gösteriyor (`data-cr-adjacent-variant-id`).

| Tip | Ürün | Option cartesian | `product.js` | Gerçek durum |
|---|---|---|---|---|
| Phone Case | 370 | 17 renk × 59 model = **1003** | 250 | Samsung ve bazı renkler API’de yok; `/variants/{id}.js` ile **var** (ör. White / Samsung S26 Ultra, Yellow / For Any iPhone) |
| Tablet Case | 231 | 16 × 54 = **864** | 250 | Tüm Samsung tablet modelleri API dışında |
| MacBook Case | 326 | 16 × 18 = **288** | 250 | Dark Green + Green Army API’de yok |

Pilot Mom PDP: Samsung satırları `data-cr-option-available="true"` ve gerçek variant id taşıyor. Yani “Samsung tamamen yok” demek yanlış — **storefront JS ilk 250’yi kesiyor**, tema geri kalanı adjacent id ile yamalıyor.

Risk (müşteri / tema):

- `product.variants` ile çalışan herhangi bir script (analytics, feed, bazı add-to-cart yolları) Samsung / sarı / Light Blue kombinasyonunu görmez.
- Picker her Color×Model çiftini yeşil gösteriyor; **1003 kombinasyonun hepsi üretilmiş mi** storefront’tan doğrulanamıyor. Admin’de variant sayısı 250 mü 1003 mü bakmak lazım.
- Başlık “iPhone & Samsung” — Samsung modelleri picker’da duruyor; yanlış varyant ekleme riski var (renk swatch’ı “Yellow / Any iPhone”, model swatch’ı “White / Samsung S26” id’sine bağlı).

Örnek: https://www.aviationshop.com/products/pilot-mom-magsafe-iphone-case

---

## 3) Coaster 4’lü set — compare-at 8 renkte yanlış

**326 / 326** coaster aynı kalıp:

| Set | Fiyat | compare-at (doğru renkler) | compare-at (bozuk 8 renk) |
|---|---|---|---|
| 1 Piece | $13.99 | $25.98 | — |
| 4 Pieces Set | $35.99 | **$69.98** | **$25.98** (1’li fiyatı kopyalanmış) |

Bozuk renkler, her üründe aynı: White, Yellow, Light Green, Turquoise, Orange, Dark Red, Dark Green, Green Army.

8 × 326 = **2608 varyantta** compare-at satış fiyatının **altında** ($25.98 < $35.99). Tema “was”ı $25.98 gösterirse 4’lü set “indirimsiz / pahalılaşmış” görünür.

Örnek: https://www.aviationshop.com/products/roll-rate-rewrites-the-horizon-designed-coasters

---

## 4) T-Shirt description / SEO — video fallback metni

**424 / 424** Double-Side T-Shirt description’ında `<video>` + “Your browser does not support the video tag.”

Bu metin PDP accordion’da videonun altında kalabilir; **JSON-LD / meta description’a da düşüyor** (sayfa kaynağında `description` alanı video fallback ile başlıyor).

Örnek: https://www.aviationshop.com/products/roll-rate-rewrites-the-horizon-double-side-t-shirt

---

## 5) Sweatshirt / Tank Top beden etiketleri

184 sweatshirt + 176 tank top, aynı 8 beden:

- `EU/US XXL (Asian 4XL)`
- `EU/US 3XL (Asian 4XL)` ← ikisi de Asian 4XL
- `EU/US 4XL (Asian 6XL)` ← Asian 5XL atlanmış

Kopya / size-chart hatası. Varyant eksik değil.

Örnek: https://www.aviationshop.com/products/roll-rate-rewrites-the-horizon-designed-sweatshirts

---

## 6) `product_type` boş (4 ürün)

- https://www.aviationshop.com/products/bunker-gear-and-steady-hands-acrylic-luggage-tags
- https://www.aviationshop.com/products/positive-g-negative-g-all-g-acrylic-luggage-tags
- https://www.aviationshop.com/products/smoke-on-show-time-designed-key-chain
- https://www.aviationshop.com/products/swoop-low-stand-it-up-designed-key-chain

Filtre / koleksiyon otomasyonu bunları kaçırır.

---

## Tip dağılımı (5 950 ürün)

| Adet | Tip |
|---:|---|
| 454 | Luggage Tag |
| 424 | T-Shirt |
| 419 | Key Chain |
| 370 | Phone Case |
| 355 | Hoodie |
| 331 | Canvas Poster |
| 327 | Hat |
| 326 | Mouse Pad, MacBook Case, Coaster, Polo Shirt |
| 314 | Towel |
| 294 | Wall Clock |
| 231 | Tablet Case |
| 221 | Mug |
| 184 | Sweatshirt |
| 183 | Notebook |
| 181 | Bomber Jacket |
| 178 | Pillow |
| 176 | Tank Top |
| 4 | (boş tip) |

Vendor: Aviation Shop 3580, Pilot Eyes Store 2043, Piloteyes737 327.

---

## Bu taramada bakılmayanlar

Koleksiyonun kalan ~7 300 ürünü, görsel-livery uyumu, related products, mobil layout, sepet, araçlar, arama relevansı. `product.js` 250 tavanı yüzünden kılıf matrisinin tamamı Admin olmadan kapanmıyor.
