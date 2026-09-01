# Mimari — orkestrasyon vs worker

Sen (Cloud Agent / Mini Grok) **orkestrasyon** yaparsın. Sosyal post’u ve görsel persist’i **worker atar**. Shopify Admin ve Higgsfield worker değildir.

```
orkestrasyon (bu skill)
  overlay_gen.py          → PNG
  Higgsfield / GenerateImage  → ham 16:9, 1:1, 9:16
  Shopify Admin GraphQL   → article + hero metafield (article.image YOK)
        │
        ▼
workers (post + persist)
  gemini-image-worker     POST /persist-bytes   JPEG KV
  storrito-story-poster   POST /schedule        IG Story @aviatorszone
  soft-snow-c1c2          POST /feed            IG Feed @aviatorszone
  facebook-page-poster    POST /photo           FB Piloteyes737
  aviation-news-ledger    D1 pool / log
```

## Worker (post / persist / ledger)

| İş | Worker | Çağrı |
| --- | --- | --- |
| JPEG persist | `gemini-image-worker` | `POST /persist-bytes` |
| IG Story | `storrito-story-poster` | `POST /schedule` header `x-poster-secret` |
| IG Feed | `soft-snow-c1c2` | `POST /feed` Bearer, `account: aviatorszone` |
| Facebook | `facebook-page-poster` | `POST /photo` Bearer; doğrula `GET /graph?id=` |
| Ledger | `aviation-news-ledger` | `/undistributed`, `/ledger-add`, `/distributor-log` |
| Feed keşif | `news-feed-proxy` | `GET /feeds` Bearer |

Storrito.com ve Meta Graph **orkestrasyondan çağrılmaz.** `STORRITO_TOKEN` / `META_TOKEN` / `FB_PAGE_TOKEN` yalnız worker wrangler secret.

**IG Story tek kapı:** `storrito-story-poster` `POST /schedule` + `x-poster-secret`. Mini Part 2 doğrudan `storrito.com` **eski** — kopyalama.

## Orkestrasyon (worker değil)

| İş | Nerede |
| --- | --- |
| Overlay | `overlay_gen.py` (Pillow) |
| Makale | Shopify Admin GraphQL |
| Görsel üretim | Cursor GenerateImage veya Higgsfield MCP |
| HTTP kapısı | **Grok Mini yolu:** Dropbox Mini skill curl (All Worker Auth). Cursor env’e sosyal secret koyma. Drive’da secret dosyası yok. Wrangler değer okunmaz. Ayrıntı: `secrets.md`. |

KV PUT (`persist_kv.py`) yalnız `/persist-bytes` 401 ise Cloud yedek — asıl yol worker persist.
