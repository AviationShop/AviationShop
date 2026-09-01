# Cursor Automation — draft

[cursor.com/automations](https://cursor.com/automations) → New automation.

## Publisher+distributor (6×/gün)

| Ayar | Değer |
| --- | --- |
| Name | Aviation News pipeline |
| Trigger | Scheduled, timezone `Europe/Istanbul` |
| Cron | `0 0,4,8,12,16,20 * * *` |
| Repository | `AviationShop/AviationShop` |
| Pull requests | Kapalı |
| Computer use | Kapalı (görsel Cursor GenerateImage + curl) |
| Environment secrets | Yalnız Shopify + `CLOUDFLARE_API_TOKEN` (zaten var). **`WORKER_AUTH_TOKEN` / `POSTER_SECRET` env’e koyma.** Sosyal kapı = Mini skill curl (Grok bot). |
| MCP (ayrı, OAuth) | Higgsfield yedek — `higgsfield.md`; Grok Image 2 için zorunlu değil |

Prompt:

```
Run the Aviation News publisher+distributor pipeline for this slot.

Follow `.cursor/automations/aviation-news/SKILL.md` then architecture.md and secrets.md.
You orchestrate. Workers post: storrito-story-poster /schedule, soft-snow-c1c2 /feed, facebook-page-poster /photo.
HTTP gates: same path as Mini Grok — read Dropbox Mini distributor-SKILL.md Step 1 All Worker Auth and use those curl headers. Do not ask the owner to paste POSTER_SECRET into Cursor env. Do not search Drive for a secret file.
Story: POST storrito-story-poster /schedule with header x-poster-secret = that same All Worker Auth string (no "Bearer " prefix). Do not call storrito.com. Do not copy Mini Part 2 Storrito Bearer.
Overlay is overlay_gen.py. Persist via gemini-image-worker /persist-bytes. Shopify Admin and Higgsfield are not workers.
Do not call Meta Graph from the agent (Facebook worker /graph verify only).

TARGET_PUBLISHED = 3 unless the owner already confirmed 4.
Grok Image 2 via Cursor GenerateImage first; Higgsfield grok_image_2_0 backup if MCP is logged in; Gemini /generate-async last resort.
Do not set article.image. Persist images via worker /persist-bytes. No Shopify Files.
Do not run if Mac Mini publisher cron is still enabled (double-publish).
Do not open a pull request.
Write the slot report in Turkish for Onur Evitan.
Store: $SHOPIFY_FLAG_STORE / aviationshop.com News blog.
```

## Watchdog (saatlik)

| Ayar | Değer |
| --- | --- |
| Cron | `8 * * * *` Europe/Istanbul (eski :08) |
| Prompt | Follow `.cursor/automations/aviation-news/watchdog.md`. Threshold 5.0h. Turkish report. No PR. |

## Enable etmeden önce

1. Sosyal kapı Cursor env’de **yok** — Grok Mini skill (Dropbox) runtime okunur. Story = worker `/schedule` + Mini All Worker Auth → `x-poster-secret`.
2. Higgsfield isteğe bağlı yedek — Cloud MCP menüsünden login (`higgsfield.md`)
3. Mac Mini publisher/distributor/watchdog cron **kapalı**
4. Bir slot manuel (bu skill ile) yeşil
