# Publisher

Hedef: `TARGET_PUBLISHED=3`. Aday tavanı 25, 6’lık bloklar. Havuz ≥12 → hafif koşum (yalnız ≤6h breaking; yoksa `healthy_early_exit`). Havuz <12 → derin koşum. Breaking her zaman geçer.

## Step 0 — havuz + runlog

`GET /undistributed?account=piloteyes737&limit=50` (Mini skill All Worker Auth Bearer). Shopify `publisher_runlog` FAZ A.

Blog GID `gid://shopify/Blog/61149831`. Tema health (eksikse LOUD ama devam): `templates/blog.json`, `templates/article.json`, `sections/blog-news-portal.liquid`.

## Step 1 — aday

Zorunlu: (a) WebSearch (b) olay anahtarları (c) taşıyıcı süpürmesi (d) `GET /feeds?max_age_hours=96` (e) standing airline search (f) Tier-1 site rotasyonu.

Gövde feed content/summary’den. Metin yoksa düşür. Başlıktan gövde yazma.

## Step 1.5 — freshness

`original_published_date` doğrulanmış, ≤96h. Recap/eski duyuru yeni gibi basılmaz.

## Step 2 — dedup (blocking)

1. Shopify `articles(query:)` hedefli arama (son 7 gün, aynı olay → DROP). Nested `blog{articles}` kullanma.
2. `POST /dedup-check` `{candidates:[{key,title,primary_entity,secondary}]}`. Jaccard ≥0.40 veya entity-pair → DROP. Carve-out: `differentFlightEvent`, `differentRouteEvent`.
3. D1 MCP yedek: `SELECT ... WHERE primary_entity` / title tokens.

Key örneği: `singapore-airlines-daily-sin-wsi-a350-2026`.

## Step 3 — yazım (oturum içi)

500–700 kelime, 5–8 `<p>`. Spesifik fact ile başla. `/write` worker emekli.

Fact-gate: isim, sayı, alıntı, teknik iddia, uçak tipi — kaynakta yoksa sil veya atıflı yaz. Hafızadan doğrulama yok.

Başlık: `[Airline] [Action] [Number/Place] [Year]`, ilk 60 karakter kritik.

Rozet: `BREAKING` kaza · `JUST IN` duyuru · `DEVELOPING` süregelen · `AVIATION NEWS` varsayılan.

Yazar rastgele: James Holloway · Elena Vargas · Marco Bianchi · Daniel Okafor.

Tags: `airline_tag`, `aircraft_tag`, `collection:random:<handle>`, `collection:related:<aircraft-collection>`. Related yalnız uçak tipi (`airbus-a350-products` vb.). Ölümlü kazada koleksiyon CTA yok. Mega smart-collection yasak: `best-selling-products`, `newest-products`, `spently_products`, `best-sellers`, `jackets-hoodies`. Random handle ≥100 ürün, koşumda tekrar etme.

Kaynak satırı gövde sonunda `Sources: …`.

## Step 4 — görseller

`image-chain.md`. QC: worker `/qc` advisory; yetkili kapı görsel Read (anatomi, logo, tip, 9:16 rotasyon). 9:16 yatık/ters = hard-fail. Aspect başına max 2 retry.

## Step 5 — Shopify

`articleCreate` — `image` **gönderme**. `isPublished: true`.

```graphql
mutation CreateArticle($article: ArticleCreateInput!) {
  articleCreate(article: $article) {
    article { id title handle publishedAt }
    userErrors { field message }
  }
}
```

Sonra `metafieldsSet`:

- ownerId article GID
- namespace `aviation_news` key `hero_image_url` type `url`
- value = 16:9 persist URL (birebir)

Geri oku. Uyuşmazlıkta LOUD; `article.image` ile kurtarma yok.

Photography-pool `/add` best-effort. Title `{aircraft} in {airline} Livery at {Setting}` ≤70. Haber fiili/tarih/emoji yok.

## Step 6 — ledger

`POST /ledger-add` curl + Bearer. `inserted:1`. `duplicate_title` → Shopify `articleDelete`, zorla insert yok.

Zorunlu alanlar: `key, title, handle` (yanıttaki gerçek handle), `article_id, published_at` (UTC ISO+Z, TR-local+Z yasak), `badge, topic, primary_entity, secondary, aircraft, airline_tag, aircraft_tag, summary, images{featured_16_9,raw_1_1,raw_9_16}, piloteyes{caption,sources_short}, aviatorszone{caption}, source_urls[], source:"news"`.

Caption ≥500 karakter. Marka hashtag yok (`#singaporeairlines` sil). Uçak tipi hashtag kalabilir (`#airbusa350`).

## TITLELOCK

Kısaltılmış final başlıkla `/dedup-check` tekrarı.
