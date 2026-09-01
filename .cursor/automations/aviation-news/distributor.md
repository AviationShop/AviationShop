# Distributor (same pipeline, after publish)

Orkestrasyon: overlay Python + persist worker + **sosyal worker POST**. Sen Storrito.com / Graph’a gitmezsin. Mimari: `architecture.md`.

Overlay + JPEG persist **her zaman** (raw 1:1 ve 9:16 var, age ≤96h). Kapı yoksa worker POST yok; sahte 4/4 yok. Twitter sentinel yalnız X.

## Step 0

`GET /undistributed?account=piloteyes737&limit=20` (ledger Bearer). DESC → **oldest-first** `published_at`. Cache-bust: `&nocache=1&_ts=`.

`source==facts` / badge `AVIATION 101` → sosyal yok. `raw_1_1` veya `raw_9_16` boş / `age_h > 96` → atla.

Cap: `_take = 4 if n>=8 else (3 if n>=4 else (2 if n in (2,3) else n))`.

## Overlay (burada, worker değil)

`overlay_gen.py` — story = `raw_9_16` → 1080×1920; feed = `raw_1_1` → 1080×1080. `featured_16_9` kaynak değil.

```bash
python3 overlay_gen.py --raw <URL> --aspect story --title "<FULL TITLE>" --badge JUST_IN --sources "Simple Flying" --out story.png
```

JPEG → `POST gemini-image-worker /persist-bytes`. 401 ise `persist_kv.py`. Letterbox → exit 3.

## Kanallar — post’u worker atar (ledger account hep `piloteyes737`)

| Kanal | Worker | Not |
| --- | --- | --- |
| IG Story | `storrito-story-poster` `POST /schedule` `x-poster-secret` | body: `instagramUsername: aviatorszone` (lowercase), `storyPostUuid` uuid5(key), `storyOverlayUrl`, `articleUrl`, `sourcesLine`. **Direkt storrito.com yok.** |
| IG Feed | `soft-snow-c1c2` `POST /feed` Bearer | `account: aviatorszone`, caption ≥500 |
| Facebook | `facebook-page-poster` `POST /photo` Bearer | sayfa Piloteyes737; `post_id` `^1537617809874772_\d+$`; `GET /graph?id=` `is_published` |
| Twitter | sentinel | `external_id: twitter-disabled-blocked`. IG/FB fail iken 4/4 sayılmaz. |

Pre-flight: `GET /distributor-log?story_key=&channel=&account=piloteyes737`. DONE=4 skip. 1–3 yalnız eksik.

Log: `POST /distributor-log` ledger worker. 4/4 olunca havuzdan düşer.

`instagramUsername` büyük harf → “not connected”.
