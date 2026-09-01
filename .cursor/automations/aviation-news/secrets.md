# Secrets and auth gates

İki katman. Karıştırma.

**Katman A — Worker wrangler secrets (zaten duruyor, 2026-09-01 CF API `.../secrets` listesi).** Değerler write-only; API/wrangler okumaz. Worker bunları **kendi içinde** Storrito/Meta’ya giderken kullanır.

| Worker | Secret adları (değer yok) |
| --- | --- |
| `storrito-story-poster` | `POSTER_SECRET`, `STORRITO_TOKEN` (`/health` → `configured:true`) |
| `soft-snow-c1c2` | `WORKER_SECRET`, `META_TOKEN` |
| `facebook-page-poster` | `WORKER_SECRET`, `FB_PAGE_TOKEN` |
| `aviation-news-ledger` | `AUTH_TOKEN` |
| `gemini-image-worker` | `WORKER_SECRET`, `GEMINI_API_KEY`, … |
| `news-feed-proxy` | `WORKER_SECRET` |

`STORRITO_TOKEN` / `META_TOKEN` / `FB_PAGE_TOKEN` **Cursor env’e kopyalanmaz.** Worker zaten kullanıyor.

**Katman B — HTTP kapısı.** Public `workers.dev` çağrısı önce kapıyı ister. Kod:

- Storrito: `x-poster-secret === env.POSTER_SECRET` değilse 401 (`STORRITO_TOKEN`’a hiç dokunulmaz)
- IG/FB: `Authorization: Bearer ${env.WORKER_SECRET}` değilse 401 (`META_TOKEN` / `FB_PAGE_TOKEN` kullanılmaz)
- Ledger: `Bearer ${env.AUTH_TOKEN}`

Cloud Agent worker’ın `env`’ine giremez. Kapı değerini header’da göstermek zorunda. `CLOUDFLARE_API_TOKEN` bu kapı **değil** (aynı uçlar 401).

Cursor env’e kopyalanacak olan **yalnız kapı** (Mac Mini’deki aynı string; rotate etme):

| Cursor env | Worker’daki ad |
| --- | --- |
| `WORKER_AUTH_TOKEN` | `AUTH_TOKEN` / `WORKER_SECRET` (paylaşılan Bearer) |
| `POSTER_SECRET` | `storrito-story-poster` `POSTER_SECRET` |

## Env (Cursor Cloud Environment)

Shopify + `WORKER_AUTH_TOKEN` + `POSTER_SECRET` yukarıdaki kapı tablosunda. `CLOUDFLARE_API_TOKEN` zaten env’de (D1/KV admin). Tema token haber yayını için gerekmez.

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
  'https://aviation-news-ledger.oevitan.workers.dev/undistributed?account=piloteyes737&limit=5'
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

Env secret **değil**. OAuth. Cloud’da bağlamak: `higgsfield.md` (cursor.com/agents → MCP).

Görsel KATMAN 1: Cursor GenerateImage (Grok Image 2). KATMAN 2 (yedek): Higgsfield `grok_image_2_0`. 401 → `higgsfield_unavailable: yes`, Grok ile devam. KATMAN 3 Higgsfield `gpt_image_2` / `nano_banana_pro`. KATMAN 4 Gemini `/generate-async` **yalnız last resort** ve `WORKER_AUTH_TOKEN` ister.

## Persist

Kaynak gerçek: `POST /persist-bytes` (Bearer) → yanıt `url` birebir kopya.

`img.aviationshop.com` WAF 403 verebilir; canlı ledger kayıtları `https://gemini-image-worker.oevitan.workers.dev/img/<uuid>.jpg` kullanır. Persist yanıtındaki host’u koru — URL uydurma yasak.

`POST /persist-bytes` 401 ise: `persist_kv.py` (CF API → KV `IMAGES` `c9e746e2b819485fa95ff5b0a2e986e8`) + GET 200 `image/jpeg`. Ledger: D1 `aviation-blog` SQL INSERT (aynı token). Feed: RSS doğrudan (proxy Bearer yoksa). Gemini `/generate-async` hâlâ worker Bearer ister.

## Rotate vs copy

Kapı string’ini Mac Mini’den Cursor env’e **kopyala**. Worker secret’ı `wrangler secret put` ile döndürme — Mini’yi kırar.
