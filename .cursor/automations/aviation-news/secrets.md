# Secrets and auth gates

İki katman. Karıştırma.

**Drive / Dropbox’ta secret arama.** Secret Drive’a konmaz. Boş Drive taraması doğru sonuçtur, hata değil. Mini Part 2’deki doğrudan Storrito Bearer **eski yol** — kopyalama. `STORRITO_TOKEN` yalnız Worker wrangler secret.

## Katman A — Worker wrangler secrets (ad listesi, değer yok)

Doğrulama: Cloudflare API `.../workers/scripts/<name>/secrets` veya `wrangler secret list`. Değerler write-only; API/wrangler okumaz. Worker bunları **kendi içinde** Storrito/Meta’ya giderken kullanır.

2026-09-01 `storrito-story-poster` listesi: `POSTER_SECRET`, `STORRITO_TOKEN`. `/health` → `{ok:true, configured:true}`.

| Worker | Secret adları (değer yok) |
| --- | --- |
| `storrito-story-poster` | `POSTER_SECRET`, `STORRITO_TOKEN` |
| `soft-snow-c1c2` | `WORKER_SECRET`, `META_TOKEN` |
| `facebook-page-poster` | `WORKER_SECRET`, `FB_PAGE_TOKEN` |
| `aviation-news-ledger` | `AUTH_TOKEN` |
| `gemini-image-worker` | `WORKER_SECRET`, `GEMINI_API_KEY`, … |
| `news-feed-proxy` | `WORKER_SECRET` |

`STORRITO_TOKEN` / `META_TOKEN` / `FB_PAGE_TOKEN` **orkestrasyona kopyalanmaz.** Sen worker’a HTTP kapısını gösterirsin; post’u worker atar.

## Katman B — HTTP kapısı (orkestrasyon → worker)

Public `workers.dev`. **Repoya token yazma.** `CLOUDFLARE_API_TOKEN` kapı değil (Workers/D1/KV admin).

| İş | Kapı | Worker |
| --- | --- | --- |
| IG Story | header `x-poster-secret` = Cursor env `POSTER_SECRET` | `storrito-story-poster` `POST /schedule` |
| IG Feed / FB | `Authorization: Bearer ${WORKER_AUTH_TOKEN}` | `soft-snow-c1c2` / `facebook-page-poster` |
| Ledger / persist | Bearer `AUTH_TOKEN` / `WORKER_SECRET` | ledger / gemini-image-worker |

Story kapısı ledger AUTH ile **aynı değil** (AUTH → 401).

**Tek Story kapısı (2026-09-01 20:30 Europe/Istanbul’dan itibaren):** `https://storrito-story-poster.oevitan.workers.dev/schedule` + `x-poster-secret`. Orkestrasyon `storrito.com` çağırmaz. Mini Part 2 `Authorization: Bearer … storrito.com/api/v1/schedule-instagram-story` kopyalanmaz.

Wrangler secret list **değer vermez**. Canlı POST için `POSTER_SECRET` Cursor Cloud Environment’e owner tarafından konur.

| Cursor env | Worker’daki ad |
| --- | --- |
| `WORKER_AUTH_TOKEN` | `AUTH_TOKEN` / `WORKER_SECRET` (paylaşılan Bearer) |
| `POSTER_SECRET` | `storrito-story-poster` `POSTER_SECRET` |

## Env (Cursor Cloud Environment)

Shopify + `WORKER_AUTH_TOKEN` + `POSTER_SECRET`. `CLOUDFLARE_API_TOKEN` zaten env’de (D1/KV admin). Tema token haber yayını için gerekmez.

## Smoke (her koşunun başı)

Browser User-Agent zorunlu. urllib/requests Cloudflare 1010 yiyebilir → `curl`.

```bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

# public — auth kanıtı değil
curl -sS -A "$UA" https://aviation-news-ledger.oevitan.workers.dev/health
curl -sS -A "$UA" https://news-feed-proxy.oevitan.workers.dev/health
curl -sS -A "$UA" https://gemini-image-worker.oevitan.workers.dev/health
curl -sS -A "$UA" https://storrito-story-poster.oevitan.workers.dev/health
# beklenen: {"ok":true,"configured":true}

# authenticated — 401 ise DUR, yayınlama
curl -sS -A "$UA" -H "Authorization: Bearer $WORKER_AUTH_TOKEN" \
  'https://news-feed-proxy.oevitan.workers.dev/feeds?max_age_hours=96&nocache=1'
curl -sS -A "$UA" -H "Authorization: Bearer $WORKER_AUTH_TOKEN" \
  'https://aviation-news-ledger.oevitan.workers.dev/undistributed?account=piloteyes737&limit=5'
```

Story smoke: `POST /schedule` **yalnız** `x-poster-secret` ile. Secret yok / yanlış → `{error:unauthorized}`. `storrito.com` deneme.

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

Worker secret’ı `wrangler secret put` ile döndürme — Mini’yi kırar. Drive’dan / Mini Part 2’den Storrito Bearer **kopyalama**. Story kapısı = Cursor env `POSTER_SECRET` → header `x-poster-secret`.
