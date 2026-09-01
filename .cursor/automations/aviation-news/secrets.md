# Secrets — Grok Mini yolu (Cursor env değil)

Grok Mini secret’i Cursor Cloud Environment’e yüklemez. Skill markdown’ı okur, içindeki curl header’ı runtime’da kullanır. Cloud aynı.

**Owner’a `POSTER_SECRET` / `WORKER_AUTH_TOKEN` yapıştır deme. Cursor env’e sosyal kapı koyma.** Shopify + `CLOUDFLARE_API_TOKEN` zaten env’de (Admin GraphQL + D1/KV). Sosyal kapı orada değil.

**Drive’da secret dosyası yok.** `POSTER_SECRET.txt` taraması boş çıkar — doğru. Drive yedek; runtime değil.

## Grok bot nasıl çalışır (kopyala)

1. Koşu başında Mini skill’i oku (Dropbox, bayat Drive kopyası değil):
   - `distributor-SKILL.md` — Dropbox `id:G9fhAuLmM4wAAAAAAB-8NQ`
     path `/@ Claude/@ MAC MINI AUTOMATIONS/Aviation News Publisher/distributor-SKILL.md`
   - `distributor-SKILL-post.md` — Dropbox `id:G9fhAuLmM4wAAAAAAB-8Lw`
2. Step 1 **All Worker Auth** satırındaki `Authorization: Bearer …` değerini al.
3. Ledger / persist / IG Feed / Facebook çağrılarına **aynı** Bearer’ı koy.
4. Token’ı git’e, PR’ye, owner raporuna yazma.

Drive launcher (Aug 31) kanonik runtime’ı Mini disk sanır. Cloud’da disk yok → Dropbox skill = Grok’un okuduğu metin.

## Katman A — Worker wrangler (ad listesi, değer yok)

Doğrulama: Cloudflare `.../workers/scripts/<name>/secrets`. Değer write-only. Worker Storrito/Meta’ya **kendi içinde** gider.

| Worker | Secret adları |
| --- | --- |
| `storrito-story-poster` | `POSTER_SECRET`, `STORRITO_TOKEN` |
| `soft-snow-c1c2` | `WORKER_SECRET`, `META_TOKEN` |
| `facebook-page-poster` | `WORKER_SECRET`, `FB_PAGE_TOKEN` |
| `aviation-news-ledger` | `AUTH_TOKEN` |
| `gemini-image-worker` | `WORKER_SECRET`, `GEMINI_API_KEY`, … |
| `news-feed-proxy` | `WORKER_SECRET` |

`STORRITO_TOKEN` / `META_TOKEN` / `FB_PAGE_TOKEN` orkestrasyona kopyalanmaz.

## Katman B — HTTP kapısı (orkestrasyon → worker)

Kaynak: Mini skill curl. `CLOUDFLARE_API_TOKEN` kapı değil (Workers/D1/KV admin; worker HTTP 401).

| İş | Header | Değer nereden | Worker |
| --- | --- | --- | --- |
| IG Story | `x-poster-secret` (**Bearer kelimesi yok**) | Mini skill **All Worker Auth** (aynı string) | `storrito-story-poster` `POST /schedule` |
| IG Feed / FB / persist / ledger / feeds | `Authorization: Bearer …` | Mini skill **All Worker Auth** | `soft-snow-c1c2` / `facebook-page-poster` / ledger / gemini-image-worker / news-feed-proxy |

2026-09-01: Story worker `POSTER_SECRET` Mini All Worker Auth ile hizalandı. Grok Feed/FB/ledger için zaten bu string’i kullanıyor. Cloud Story’de header **adı** farklı (`x-poster-secret`), **değer** aynı skill satırı.

Mini Part 2 hâlâ `storrito.com/api/v1/schedule-instagram-story` + Storrito Bearer gösterir. **Eski yol.** Cloud o URL’ye gitmez; Storrito Bearer’ı kopyalamaz. `STORRITO_TOKEN` worker’da kalır.

## Story (tek kapı)

`https://storrito-story-poster.oevitan.workers.dev/schedule` + `x-poster-secret`.

Mini skill AUTH’u `Authorization: Bearer` diye Story worker’a gönderme — header adı `x-poster-secret`. Yanlış header → `{error:unauthorized}`.

`/health` → `{ok:true,configured:true}` auth kanıtı değil (public). Auth kanıtı: boş `{}` POST doğru secret ile **401 değil** (username yoksa 400).

## Smoke (her koşunun başı)

Browser UA. urllib/requests → CF 1010 → `curl`.

Kapıyı Mini skill’den oku; aşağıda `$GATE` = All Worker Auth string (Bearer’sız).

```bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

curl -sS -A "$UA" https://aviation-news-ledger.oevitan.workers.dev/health
curl -sS -A "$UA" https://storrito-story-poster.oevitan.workers.dev/health
# public: {"ok":true,"configured":true}

curl -sS -A "$UA" -H "Authorization: Bearer $GATE" \
  'https://news-feed-proxy.oevitan.workers.dev/feeds?max_age_hours=96&nocache=1'
curl -sS -A "$UA" -H "Authorization: Bearer $GATE" \
  'https://aviation-news-ledger.oevitan.workers.dev/undistributed?account=piloteyes737&limit=5'
```

401 → Mini skill’i yeniden oku, yayınlama. Cursor env’de arama. Owner’a secret yapıştır deme.

Story smoke: `POST /schedule` yalnız `x-poster-secret: $GATE`. `storrito.com` deneme.

## Shopify Admin

Cursor env: `SHOPIFY_APP_CLIENT_ID` / `SHOPIFY_APP_CLIENT_SECRET` / `SHOPIFY_FLAG_STORE`.

```
POST https://{SHOPIFY_FLAG_STORE}/admin/oauth/access_token
{ "grant_type":"client_credentials", "client_id":..., "client_secret":... }
```

Token ~24h. Scope: `write_content`. Shop `gid://shopify/Shop/12177182`. News blog `gid://shopify/Blog/61149831`.

API sırası: `2026-07` → `2026-04` → `2025-10`. Storefront curl UA içinde **`Cursor-Store-Wander`**.

## Higgsfield MCP

Env secret değil. OAuth. `higgsfield.md`.

Görsel: Cursor GenerateImage (Grok Image 2) → Higgsfield `grok_image_2_0` yedek → `gpt_image_2` / `nano_banana_pro` → Gemini `/generate-async` last resort (Mini skill Bearer).

## Persist

`POST /persist-bytes` (Mini skill Bearer) → yanıt `url` birebir. 401 → `persist_kv.py` (CF API → KV `IMAGES` `c9e746e2b819485fa95ff5b0a2e986e8`). URL uydurma yok.

## Rotate vs copy

Worker secret’ı `wrangler secret put` ile rastgele döndürme — Mini’yi kırar. Mini Part 2 Storrito Bearer’ı `storrito.com`’a kopyalama. Story = worker + Mini skill All Worker Auth → `x-poster-secret`.
