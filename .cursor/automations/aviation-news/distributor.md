# Distributor (same pipeline, after publish)

Overlay + JPEG persist **her zaman** (yayınlanan hikâye, raw 1:1 ve 9:16 var, age ≤96h).

Sosyal POST (`STORRITO_TOKEN` / `POSTER_SECRET` / Meta Bearer) yoksa **dur**: Storrito/IG/FB çağırma. Sahte 4/4 yok. Twitter sentinel (`twitter-disabled-blocked`) yalnız X kanalı. Raporda `distributor_partial: missing_social_secrets`. Overlay URL’leri `piloteyes_json.feed_overlay_url` / `story_overlay_url`.

## Step 0

`GET /undistributed?account=piloteyes737&limit=20`. Worker DESC döner → **oldest-first** sort `published_at`. Cache-bust gerekirse `&nocache=1&_ts=`.

`source==facts` / badge `AVIATION 101` → sosyal yok.

NO-CROP: `raw_1_1` veya `raw_9_16` boşsa atla. `age_h > 96` atla.

Cap: `_take = 4 if n>=8 else (3 if n>=4 else (2 if n in (2,3) else n))`.

## Overlay

`overlay_gen.py` — story = `raw_9_16` → 1080×1920; feed = `raw_1_1` → 1080×1080. `featured_16_9` overlay kaynağı değil.

```bash
python3 overlay_gen.py --raw <URL> --aspect story --title "<FULL TITLE>" --badge JUST_IN --sources "Simple Flying" --out story.png
```

JPEG persist `/persist-bytes`. Letterbox → exit 3, dosya yok.

## Kanallar (ledger account etiketi hep `piloteyes737`)

| Kanal | Hedef | Not |
| --- | --- | --- |
| IG Story | Storrito `aviatorszone` (lowercase) | HTML cover + link sticker makale URL |
| IG Feed | `soft-snow-c1c2.oevitan.workers.dev/feed` account `aviatorszone` | caption ≥500 |
| Facebook | `facebook-page-poster.oevitan.workers.dev/photo` | `@piloteyes737`; post_id `PAGEID_digits`; GET `/graph?id=` `is_published` |
| Twitter | **sentinel** | `external_id: twitter-disabled-blocked` status success. IG/FB fail iken 4/4 sayılmaz. |

Pre-flight: `GET /distributor-log?story_key=&channel=&account=piloteyes737`. DONE=4 skip. 1–3 yalnız eksik.

Log: `POST /distributor-log`. 4/4 olunca havuzdan düşer.

`instagramUsername` büyük harf → “not connected”.
