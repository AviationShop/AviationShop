# Distributor (same pipeline, after publish)

Orkestrasyon: overlay Python + persist worker + **sosyal worker POST**. Sen Storrito.com / Graph’a gitmezsin. Mimari: `architecture.md`.

Overlay + JPEG persist **her zaman** (raw 1:1 ve 9:16 var, age ≤96h). Kapı yoksa worker POST yok; sahte 4/4 yok. Twitter sentinel yalnız X.

## Step 0

`GET /undistributed?account=piloteyes737&limit=20` (Mini skill All Worker Auth Bearer — Grok yolu). DESC → **oldest-first** `published_at`. Cache-bust: `&nocache=1&_ts=`.

`source==facts` / badge `AVIATION 101` → sosyal yok. `raw_1_1` veya `raw_9_16` boş / `age_h > 96` → atla.

Cap: `_take = 4 if n>=8 else (3 if n>=4 else (2 if n in (2,3) else n))`.

## Overlay (burada, worker değil) — Mini kanonik, sadeleştirme YASAK

`overlay_gen.py` Mini 2026-07-24 kopyası. Story = `raw_9_16` → 1080×1920; feed = `raw_1_1` → 1080×1080. `featured_16_9` kaynak değil. Raw post yok.

**Feed (Onur şablon):** mavi pill `AVIATION NEWS` sol üst; all-caps başlık alt üçte; `Sources: AeroRoutes`; mavi bar sol `@aviatorszone` sağ `AviationShop.com | Daily Aviation News`. Caption title-case + ✈️, overlay all-caps.

**Story (Onur şablon):** AVIATION NEWS pill + all-caps başlık + mavi çizgi + `AviationShop.com | Daily Aviation News` + `✓ Sources: …`. Alt `Sources: … | AI Generated Image` ve `READ ARTICLE` sticker **Storrito worker HTML** (Pillow’a basma). Sağ alt `aviationshop.com`.

```bash
python3 overlay_gen.py --raw <raw_9_16_url> --aspect story --title "<FULL TITLE>" --badge "AVIATION NEWS" --sources "AeroRoutes" --out story.png
python3 overlay_gen.py --raw <raw_1_1_url> --aspect feed --title "<FULL TITLE>" --badge "AVIATION NEWS" --sources "AeroRoutes" --out feed.png
```

JPEG q92 → `POST gemini-image-worker /persist-bytes`. 401 ise `persist_kv.py`. Letterbox → exit 3. Worker `storyOverlayUrl` / `image_url` = **overlay persist URL**, raw değil.

## Kanallar — post’u worker atar (ledger account hep `piloteyes737`)

| Kanal | Worker | Not |
| --- | --- | --- |
| IG Story | `storrito-story-poster` `POST /schedule` header `x-poster-secret` | **Tek kapı.** Overlay persist URL. `instagramUsername: aviatorszone` (lowercase). `storyPostUuid` uuid5(key). Storrito HTML: `READ ARTICLE` sticker + `Sources: … | AI Generated Image`. `storrito.com` yok. |
| IG Feed | `soft-snow-c1c2` `POST /feed` Bearer | Mini skill All Worker Auth. `account: aviatorszone`, caption ≥500 |
| Facebook | `facebook-page-poster` `POST /photo` Bearer | Mini skill All Worker Auth. sayfa Piloteyes737; `post_id` `^1537617809874772_\d+$`; `GET /graph?id=` `is_published` |
| Twitter | sentinel | `external_id: twitter-disabled-blocked`. IG/FB fail iken 4/4 sayılmaz. |

Pre-flight: `GET /distributor-log?story_key=&channel=&account=piloteyes737`. DONE=4 skip. 1–3 yalnız eksik.

Log: `POST /distributor-log` ledger worker. 4/4 olunca havuzdan düşer.

`instagramUsername` büyük harf → “not connected”.
