# Secrets and auth gates

`CLOUDFLARE_API_TOKEN` Workers/D1/KV **admin** token’ıdır (secret **adlarını** listeler, D1 yazar, KV’ye görsel koyar). Worker HTTP Bearer (`AUTH_TOKEN` / `WORKER_SECRET`) **ayrı** bir wrangler secret’tır; değeri API’den okunmaz.

2026-09-01 test: CF token’ı `Authorization: Bearer` olarak `/feeds`, `/persist-bytes`, `/dedup-check`’e gönderince **401**. Aynı token ile `wrangler secret list` → `AUTH_TOKEN` adı görünür; KV PUT + D1 INSERT canlı yayında çalıştı.

## Env (Cursor Cloud Environment)

Zorunlu (publisher):

| Name | Role |
| --- | --- |
| `SHOPIFY_FLAG_STORE` | `$SHOPIFY_FLAG_STORE` |
| `SHOPIFY_APP_CLIENT_ID` | Admin client credentials |
| `SHOPIFY_APP_CLIENT_SECRET` | Admin client credentials |
| `WORKER_AUTH_TOKEN` | Shared Bearer. Worker tarafında `WORKER_SECRET` (gemini-image-worker, news-feed-proxy) = `AUTH_TOKEN` (ledger, image-pipeline, article-writer) |

İsteğe bağlı (distributor):

| Name | Role |
| --- | --- |
| `STORRITO_TOKEN` | IG Story `@aviatorszone` |
| Meta poster Bearer | `soft-snow-c1c2` / `facebook-page-poster` (aynı worker Bearer olabilir) |

Tema token (`SHOPIFY_CLI_THEME_TOKEN`) haber yayını için gerekmez.

## Smoke (her koşunun başı)

Browser User-Agent zorunlu. urllib/requests Cloudflare 1010 yiyebilir → `curl`.

```bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

# public
curl -sS -A "$UA" https://aviation-news-ledger.oevitan.workers.dev/health
curl -sS -A "$UA" https://news-feed-proxy.oevitan.workers.dev/health
curl -sS -A "$UA" https://gemini-image-worker.oevitan.workers.dev/health

# authenticated — 401 ise DUR, yayınlama
curl -sS -A "$UA" -H "Authorization: Bearer $WORKER_AUTH_TOKEN" \
  'https://news-feed-proxy.oevitan.workers.dev/feeds?max_age_hours=96&nocache=1'
curl -sS -A "$UA" -H "Authorization: Bearer $WORKER_AUTH_TOKEN" \
  'https://aviation-news-ledger.oevitan.workers.dev/undistributed?account=$SHOPIFY_FLAG_STORE737&limit=5'
```

`/health` public’tir; auth kanıtı **değildir**.

## Shopify Admin

```
POST https://{SHOPIFY_FLAG_STORE}/admin/oauth/access_token
{ "grant_type":"client_credentials", "client_id":..., "client_secret":... }
```

Token ~24h. Gerekli scope: `write_content`. Shop GID `gid://shopify/Shop/12177182`. News blog `gid://shopify/Blog/61149831`.

API sırası: `2026-07` → `2026-04` → `2025-10`.

## Higgsfield MCP

Görsel KATMAN 1: model id `grok_image_2_0`. Oturum 401 ise Grok zinciri ölüdür. KATMAN 2 Higgsfield yedek (`gpt_image_2` / `nano_banana_pro`). KATMAN 3 Gemini worker `/generate-async` **yalnız last resort** ve `WORKER_AUTH_TOKEN` ister.

## Persist

Kaynak gerçek: `POST /persist-bytes` (Bearer) → yanıt `url` birebir kopya.

`img.aviationshop.com` WAF 403 verebilir; canlı ledger kayıtları `https://gemini-image-worker.oevitan.workers.dev/img/<uuid>.jpg` kullanır. Persist yanıtındaki host’u koru — URL uydurma yasak.

`POST /persist-bytes` 401 ise: `persist_kv.py` (CF API → KV `IMAGES` `c9e746e2b819485fa95ff5b0a2e986e8`) + GET 200 `image/jpeg`. Ledger: D1 `aviation-blog` SQL INSERT (aynı token). Feed: RSS doğrudan (proxy Bearer yoksa). Gemini `/generate-async` hâlâ worker Bearer ister.

## Rotate vs copy

Token yoksa: Mac Mini skill’den kopyala **veya** `wrangler secret put` ile döndür. Döndürmek Mac Mini’yi anında kırar — önce Mini cron’unu kapat.
